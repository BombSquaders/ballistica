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
"""Functionality related to teams sessions."""
from __future__ import annotations

from typing import TYPE_CHECKING

import _ba
from ba import _multiteamsession

if TYPE_CHECKING:
    import ba


class DualTeamSession(_multiteamsession.MultiTeamSession):
    """ba.Session type for teams mode games.

    Category: Gameplay Classes
    """
    _use_teams = True
    _playlist_selection_var = 'Team Tournament Playlist Selection'
    _playlist_randomize_var = 'Team Tournament Playlist Randomize'
    _playlists_var = 'Team Tournament Playlists'

    def __init__(self) -> None:
        _ba.increment_analytics_count('Teams session start')
        super().__init__()

    def _switch_to_score_screen(self, results: ba.TeamGameResults) -> None:
        # pylint: disable=cyclic-import
        from bastd.activity.drawscore import DrawScoreScreenActivity
        from bastd.activity.dualteamscore import (
            TeamVictoryScoreScreenActivity)
        from bastd.activity.multiteamvictory import (
            TeamSeriesVictoryScoreScreenActivity)
        winners = results.get_winners()

        # If everyone has the same score, call it a draw.
        if len(winners) < 2:
            self.set_activity(_ba.new_activity(DrawScoreScreenActivity))
        else:
            winner = winners[0].teams[0]
            winner.sessiondata['score'] += 1

            # If a team has won, show final victory screen.
            if winner.sessiondata['score'] >= (self._series_length -
                                               1) / 2 + 1:
                self.set_activity(
                    _ba.new_activity(TeamSeriesVictoryScoreScreenActivity,
                                     {'winner': winner}))
            else:
                self.set_activity(
                    _ba.new_activity(TeamVictoryScoreScreenActivity,
                                     {'winner': winner}))
