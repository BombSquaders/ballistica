# Copyright (c) 2011-2020 Eric Froemling
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# -----------------------------------------------------------------------------
"""Implements Target Practice game."""

# ba_meta require api 6
# (see https://github.com/efroemling/ballistica/wiki/Meta-Tags)

from __future__ import annotations

import random
from typing import TYPE_CHECKING

import ba
from bastd.actor import playerspaz

if TYPE_CHECKING:
    from typing import Any, Type, List, Dict, Optional, Tuple, Sequence
    from bastd.actor.onscreencountdown import OnScreenCountdown
    from bastd.actor.bomb import Bomb, Blast


# ba_meta export game
class TargetPracticeGame(ba.TeamGameActivity):
    """Game where players try to hit targets with bombs."""

    @classmethod
    def get_name(cls) -> str:
        return 'Target Practice'

    @classmethod
    def get_description(cls, sessiontype: Type[ba.Session]) -> str:
        return 'Bomb as many targets as you can.'

    @classmethod
    def get_supported_maps(cls, sessiontype: Type[ba.Session]) -> List[str]:
        return ['Doom Shroom']

    @classmethod
    def supports_session_type(cls, sessiontype: Type[ba.Session]) -> bool:
        # We support any teams or versus sessions.
        return (issubclass(sessiontype, ba.CoopSession)
                or issubclass(sessiontype, ba.MultiTeamSession))

    @classmethod
    def get_settings(
            cls,
            sessiontype: Type[ba.Session]) -> List[Tuple[str, Dict[str, Any]]]:
        return [("Target Count", {
            'min_value': 1,
            'default': 3
        }), ("Enable Impact Bombs", {
            'default': True
        }), ("Enable Triple Bombs", {
            'default': True
        })]

    def __init__(self, settings: Dict[str, Any]):
        from bastd.actor.scoreboard import Scoreboard
        super().__init__(settings)
        self._scoreboard = Scoreboard()
        self._targets: List[Target] = []
        self._update_timer: Optional[ba.Timer] = None
        self._countdown: Optional[OnScreenCountdown] = None

    def on_transition_in(self) -> None:
        self.default_music = ba.MusicType.FORWARD_MARCH
        super().on_transition_in()

    def on_team_join(self, team: ba.Team) -> None:
        team.gamedata['score'] = 0
        if self.has_begun():
            self.update_scoreboard()

    def on_begin(self) -> None:
        from bastd.actor.onscreencountdown import OnScreenCountdown
        super().on_begin()
        self.update_scoreboard()

        # Number of targets is based on player count.
        num_targets = self.settings['Target Count']
        for i in range(num_targets):
            ba.timer(5.0 + i * 1.0, self._spawn_target)

        self._update_timer = ba.Timer(1.0, self._update, repeat=True)
        self._countdown = OnScreenCountdown(60, endcall=self.end_game)
        ba.timer(4.0, self._countdown.start)

    def spawn_player(self, player: ba.Player) -> ba.Actor:
        spawn_center = (0, 3, -5)
        pos = (spawn_center[0] + random.uniform(-1.5, 1.5), spawn_center[1],
               spawn_center[2] + random.uniform(-1.5, 1.5))

        # Reset their streak.
        player.gamedata['streak'] = 0
        spaz = self.spawn_player_spaz(player, position=pos)

        # Give players permanent triple impact bombs and wire them up
        # to tell us when they drop a bomb.
        if self.settings['Enable Impact Bombs']:
            spaz.bomb_type = 'impact'
        if self.settings['Enable Triple Bombs']:
            spaz.set_bomb_count(3)
        spaz.add_dropped_bomb_callback(self._on_spaz_dropped_bomb)
        return spaz

    def _spawn_target(self) -> None:

        # Generate a few random points; we'll use whichever one is farthest
        # from our existing targets (don't want overlapping targets).
        points = []

        for _i in range(4):
            # Calc a random point within a circle.
            while True:
                xpos = random.uniform(-1.0, 1.0)
                ypos = random.uniform(-1.0, 1.0)
                if xpos * xpos + ypos * ypos < 1.0:
                    break
            points.append((8.0 * xpos, 2.2, -3.5 + 5.0 * ypos))

        def get_min_dist_from_target(pnt: Sequence[float]) -> float:
            return min((t.get_dist_from_point(pnt) for t in self._targets))

        # If we have existing targets, use the point with the highest
        # min-distance-from-targets.
        if self._targets:
            point = max(points, key=get_min_dist_from_target)
        else:
            point = points[0]

        self._targets.append(Target(position=point))

    # noinspection PyUnusedLocal
    def _on_spaz_dropped_bomb(self, spaz: ba.Actor, bomb: ba.Actor) -> None:
        # pylint: disable=unused-argument
        from bastd.actor.bomb import Bomb

        # Wire up this bomb to inform us when it blows up.
        assert isinstance(bomb, Bomb)
        bomb.add_explode_callback(self._on_bomb_exploded)

    def _on_bomb_exploded(self, bomb: Bomb, blast: Blast) -> None:
        assert blast.node
        pos = blast.node.position

        # Debugging: throw a locator down where we landed.
        # ba.newnode('locator', attrs={'position':blast.node.position})

        # Feed the explosion point to all our targets and get points in return.
        # Note: we operate on a copy of self._targets since the list may change
        # under us if we hit stuff (don't wanna get points for new targets).
        player = bomb.get_source_player()
        if not player:
            return  # could happen if they leave after throwing a bomb..

        bullseye = any(
            target.do_hit_at_position(pos, player)
            for target in list(self._targets))
        if bullseye:
            player.gamedata['streak'] += 1
        else:
            player.gamedata['streak'] = 0

    def _update(self) -> None:
        """Misc. periodic updating."""
        # Clear out targets that have died.
        self._targets = [t for t in self._targets if t]

    def handlemessage(self, msg: Any) -> Any:
        # When players die, respawn them.
        if isinstance(msg, playerspaz.PlayerSpazDeathMessage):
            super().handlemessage(msg)  # Do standard stuff.
            player = msg.spaz.getplayer()
            assert player is not None
            self.respawn_player(player)  # Kick off a respawn.
        elif isinstance(msg, Target.TargetHitMessage):
            # A target is telling us it was hit and will die soon..
            # ..so make another one.
            self._spawn_target()
        else:
            super().handlemessage(msg)

    def update_scoreboard(self) -> None:
        """Update the game scoreboard with current team values."""
        for team in self.teams:
            self._scoreboard.set_team_value(team, team.gamedata['score'])

    def end_game(self) -> None:
        results = ba.TeamGameResults()
        for team in self.teams:
            results.set_team_score(team, team.gamedata['score'])
        self.end(results)


class Target(ba.Actor):
    """A target practice target."""

    class TargetHitMessage:
        """Inform an object a target was hit."""

    def __init__(self, position: Sequence[float]):
        self._r1 = 0.45
        self._r2 = 1.1
        self._r3 = 2.0
        self._rfudge = 0.15
        super().__init__()
        self._position = ba.Vec3(position)
        self._hit = False

        # It can be handy to test with this on to make sure the projection
        # isn't too far off from the actual object.
        show_in_space = False
        loc1 = ba.newnode('locator',
                          attrs={
                              'shape': 'circle',
                              'position': position,
                              'color': (0, 1, 0),
                              'opacity': 0.5,
                              'draw_beauty': show_in_space,
                              'additive': True
                          })
        loc2 = ba.newnode('locator',
                          attrs={
                              'shape': 'circle_outline',
                              'position': position,
                              'color': (0, 1, 0),
                              'opacity': 0.3,
                              'draw_beauty': False,
                              'additive': True
                          })
        loc3 = ba.newnode('locator',
                          attrs={
                              'shape': 'circle_outline',
                              'position': position,
                              'color': (0, 1, 0),
                              'opacity': 0.1,
                              'draw_beauty': False,
                              'additive': True
                          })
        self._nodes = [loc1, loc2, loc3]
        ba.animate_array(loc1, 'size', 1, {0: [0.0], 0.2: [self._r1 * 2.0]})
        ba.animate_array(loc2, 'size', 1, {
            0.05: [0.0],
            0.25: [self._r2 * 2.0]
        })
        ba.animate_array(loc3, 'size', 1, {0.1: [0.0], 0.3: [self._r3 * 2.0]})
        ba.playsound(ba.getsound('laserReverse'))

    def exists(self) -> bool:
        return bool(self._nodes)

    def handlemessage(self, msg: Any) -> Any:
        if isinstance(msg, ba.DieMessage):
            for node in self._nodes:
                node.delete()
            self._nodes = []
        else:
            super().handlemessage(msg)

    def get_dist_from_point(self, pos: Sequence[float]) -> float:
        """Given a point, returns distance squared from it."""
        return (ba.Vec3(pos) - self._position).length()

    def do_hit_at_position(self, pos: Sequence[float],
                           player: ba.Player) -> bool:
        """Handle a bomb hit at the given position."""
        # pylint: disable=too-many-statements
        from bastd.actor import popuptext
        activity = self.activity

        # Ignore hits if the game is over or if we've already been hit
        if activity.has_ended() or self._hit or not self._nodes:
            return False

        diff = (ba.Vec3(pos) - self._position)

        # Disregard Y difference. Our target point probably isn't exactly
        # on the ground anyway.
        diff[1] = 0.0
        dist = diff.length()

        bullseye = False
        if dist <= self._r3 + self._rfudge:
            # Inform our activity that we were hit
            self._hit = True
            activity.handlemessage(self.TargetHitMessage())
            keys: Dict[float, Sequence[float]] = {
                0.0: (1.0, 0.0, 0.0),
                0.049: (1.0, 0.0, 0.0),
                0.05: (1.0, 1.0, 1.0),
                0.1: (0.0, 1.0, 0.0)
            }
            cdull = (0.3, 0.3, 0.3)
            popupcolor: Sequence[float]
            if dist <= self._r1 + self._rfudge:
                bullseye = True
                self._nodes[1].color = cdull
                self._nodes[2].color = cdull
                ba.animate_array(self._nodes[0], 'color', 3, keys, loop=True)
                popupscale = 1.8
                popupcolor = (1, 1, 0, 1)
                streak = player.gamedata['streak']
                points = 10 + min(20, streak * 2)
                ba.playsound(ba.getsound('bellHigh'))
                if streak > 0:
                    ba.playsound(
                        ba.getsound(
                            'orchestraHit4' if streak > 3 else
                            'orchestraHit3' if streak > 2 else
                            'orchestraHit2' if streak > 1 else 'orchestraHit'))
            elif dist <= self._r2 + self._rfudge:
                self._nodes[0].color = cdull
                self._nodes[2].color = cdull
                ba.animate_array(self._nodes[1], 'color', 3, keys, loop=True)
                popupscale = 1.25
                popupcolor = (1, 0.5, 0.2, 1)
                points = 4
                ba.playsound(ba.getsound('bellMed'))
            else:
                self._nodes[0].color = cdull
                self._nodes[1].color = cdull
                ba.animate_array(self._nodes[2], 'color', 3, keys, loop=True)
                popupscale = 1.0
                popupcolor = (0.8, 0.3, 0.3, 1)
                points = 2
                ba.playsound(ba.getsound('bellLow'))

            # Award points/etc.. (technically should probably leave this up
            # to the activity).
            popupstr = "+" + str(points)

            # If there's more than 1 player in the game, include their
            # names and colors so they know who got the hit.
            if len(activity.players) > 1:
                popupcolor = ba.safecolor(player.color, target_intensity=0.75)
                popupstr += ' ' + player.get_name()
            popuptext.PopupText(popupstr,
                                position=self._position,
                                color=popupcolor,
                                scale=popupscale).autoretain()

            # Give this player's team points and update the score-board.
            player.team.gamedata['score'] += points
            assert isinstance(activity, TargetPracticeGame)
            activity.update_scoreboard()

            # Also give this individual player points
            # (only applies in teams mode).
            assert activity.stats is not None
            activity.stats.player_scored(player,
                                         points,
                                         showpoints=False,
                                         screenmessage=False)

            ba.animate_array(self._nodes[0], 'size', 1, {
                0.8: self._nodes[0].size,
                1.0: [0.0]
            })
            ba.animate_array(self._nodes[1], 'size', 1, {
                0.85: self._nodes[1].size,
                1.05: [0.0]
            })
            ba.animate_array(self._nodes[2], 'size', 1, {
                0.9: self._nodes[2].size,
                1.1: [0.0]
            })
            ba.timer(1.1, ba.Call(self.handlemessage, ba.DieMessage()))

        return bullseye
