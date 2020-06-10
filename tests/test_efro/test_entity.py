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
"""Testing entity functionality."""

from __future__ import annotations

from typing import TYPE_CHECKING
from enum import Enum, unique

import pytest

from efro import entity
from efrotools.statictest import static_type_equals

if TYPE_CHECKING:
    pass


@unique
class EnumTest(Enum):
    """Testing..."""
    FIRST = 0
    SECOND = 1


class SubCompoundTest(entity.CompoundValue):
    """Testing..."""
    subval = entity.Field('b', entity.BoolValue())


class CompoundTest(entity.CompoundValue):
    """Testing..."""
    isubval = entity.Field('i', entity.IntValue(default=34532))
    compoundlist = entity.CompoundListField('l', SubCompoundTest())


class CompoundTest2(CompoundTest):
    """Testing..."""
    isubval2 = entity.Field('i2', entity.IntValue(default=3453))


class EntityTest(entity.Entity):
    """Testing..."""
    ival = entity.Field('i', entity.IntValue(default=345))
    sval = entity.Field('s', entity.StringValue(default='svvv'))
    bval = entity.Field('b', entity.BoolValue(default=True))
    fval = entity.Field('f', entity.FloatValue(default=1.0))
    grp = entity.CompoundField('g', CompoundTest())
    grp2 = entity.CompoundField('g2', CompoundTest2())
    enumval = entity.Field('e', entity.EnumValue(EnumTest, default=None))
    enumval2 = entity.Field(
        'e2', entity.OptionalEnumValue(EnumTest, default=EnumTest.SECOND))
    slval = entity.ListField('sl', entity.StringValue())
    tval2 = entity.Field('t2', entity.DateTimeValue())
    str_int_dict = entity.DictField('sd', str, entity.IntValue())
    compoundlist = entity.CompoundListField('l', CompoundTest())
    compoundlist2 = entity.CompoundListField('l2', CompoundTest())
    compoundlist3 = entity.CompoundListField('l3', CompoundTest2())
    compounddict = entity.CompoundDictField('td', str, CompoundTest())
    compounddict2 = entity.CompoundDictField('td2', str, CompoundTest())
    compounddict3 = entity.CompoundDictField('td3', str, CompoundTest2())
    fval2 = entity.Field('f2', entity.Float3Value())


# noinspection PyTypeHints
def test_entity_values() -> None:
    """Test various entity assigns for value and type correctness."""
    ent = EntityTest()

    # Simple int field.
    with pytest.raises(TypeError):
        ent.ival = 'strval'  # type: ignore
    assert static_type_equals(ent.ival, int)
    assert isinstance(ent.ival, int)
    assert ent.ival == 345
    ent.ival = 346
    assert ent.ival == 346

    # Simple float field.
    with pytest.raises(TypeError):
        ent.fval = 'foo'  # type: ignore
    assert static_type_equals(ent.fval, float)
    ent.fval = 2
    ent.fval = True
    ent.fval = 1.0

    # Simple value list field.
    assert not ent.slval
    assert len(ent.slval) == 0
    with pytest.raises(TypeError):
        ent.slval.append(1)  # type: ignore
    ent.slval.append('blah')
    assert len(ent.slval) == 1
    assert list(ent.slval) == ['blah']
    with pytest.raises(TypeError):
        ent.slval = ['foo', 'bar', 1]  # type: ignore

    # Simple value dict field.
    assert 'foo' not in ent.str_int_dict
    # Set with incorrect key type should give TypeError.
    with pytest.raises(TypeError):
        ent.str_int_dict[0] = 123  # type: ignore
    # And set with incorrect value type should do same.
    with pytest.raises(TypeError):
        ent.str_int_dict['foo'] = 'bar'  # type: ignore
    ent.str_int_dict['foo'] = 123
    assert static_type_equals(ent.str_int_dict['foo'], int)
    assert ent.str_int_dict['foo'] == 123

    # Waaah; this works at runtime, but it seems that we'd need
    # to have BoundDictField inherit from Mapping for mypy to accept this.
    # (which seems to get a bit ugly, but may be worth revisiting)
    # assert dict(ent.str_int_dict) == {'foo': 123}

    # Passing key/value pairs as a list works though..
    assert dict(ent.str_int_dict.items()) == {'foo': 123}


# noinspection PyTypeHints
def test_entity_values_2() -> None:
    """Test various entity assigns for value and type correctness."""

    ent = EntityTest()

    # Compound value
    assert static_type_equals(ent.grp, CompoundTest)
    assert static_type_equals(ent.grp.isubval, int)
    assert isinstance(ent.grp.isubval, int)
    with pytest.raises(TypeError):
        ent.grp.isubval = 'blah'  # type: ignore

    # Compound value inheritance.
    assert ent.grp2.isubval2 == 3453
    assert ent.grp2.isubval == 34532

    # Compound list field.
    with pytest.raises(IndexError):
        print(ent.compoundlist[0])
    with pytest.raises(TypeError):
        ent.compoundlist[0] = 123  # type: ignore
    assert len(ent.compoundlist) == 0
    assert not ent.compoundlist
    ent.compoundlist.append()
    assert ent.compoundlist
    assert len(ent.compoundlist) == 1
    assert static_type_equals(ent.compoundlist[0], CompoundTest)

    # Compound dict field.
    cdval = ent.compounddict.add('foo')
    assert static_type_equals(cdval, CompoundTest)
    # Set with incorrect key type should give TypeError.
    with pytest.raises(TypeError):
        _cdval2 = ent.compounddict.add(1)  # type: ignore
    # Hmm; should this throw a TypeError and not a KeyError?..
    with pytest.raises(KeyError):
        _cdval3 = ent.compounddict[1]  # type: ignore
    assert static_type_equals(ent.compounddict['foo'], CompoundTest)

    # Enum value
    with pytest.raises(ValueError):
        ent.enumval = None  # type: ignore
    assert ent.enumval == EnumTest.FIRST

    # Optional Enum value
    ent.enumval2 = None
    assert ent.enumval2 is None

    # Nested compound values
    assert not ent.grp.compoundlist
    val = ent.grp.compoundlist.append()
    assert static_type_equals(val, SubCompoundTest)
    assert static_type_equals(ent.grp.compoundlist[0], SubCompoundTest)
    assert static_type_equals(ent.grp.compoundlist[0].subval, bool)


# noinspection PyTypeHints
def test_field_copies() -> None:
    """Test copying various values between fields."""
    ent1 = EntityTest()
    ent2 = EntityTest()

    # Copying a simple value.
    ent1.ival = 334
    ent2.ival = ent1.ival
    assert ent2.ival == 334

    # Copying a nested compound.
    ent1.grp.isubval = 543
    ent2.grp = ent1.grp
    assert ent2.grp.isubval == 543

    # Type-checker currently allows this because both are Compounds
    # but should fail at runtime since their subfield arrangement differs.
    # reveal_type(ent1.grp.blah)
    with pytest.raises(ValueError):
        ent2.grp = ent1.grp2

    # Copying a value list.
    ent1.slval = ['foo', 'bar']
    assert ent1.slval == ['foo', 'bar']
    ent2.slval = ent1.slval
    assert ent2.slval == ['foo', 'bar']

    # Copying a value dict.
    ent1.str_int_dict['tval'] = 987
    ent2.str_int_dict = ent1.str_int_dict
    assert ent2.str_int_dict['tval'] == 987

    # Copying a CompoundList
    val = ent1.compoundlist.append()
    val.isubval = 356
    assert ent1.compoundlist[0].isubval == 356
    assert len(ent1.compoundlist) == 1
    ent1.compoundlist.append()
    assert len(ent1.compoundlist) == 2
    assert len(ent2.compoundlist) == 0
    # Copying to the same field on different obj should work.
    ent2.compoundlist = ent1.compoundlist
    assert ent2.compoundlist[0].isubval == 356
    assert len(ent2.compoundlist) == 2
    # Cross-field assigns should work too if the field layouts match..
    ent1.compoundlist2 = ent1.compoundlist
    # And not if they don't...
    # (in this case mypy errors too but that may not always be the case)
    with pytest.raises(ValueError):
        ent1.compoundlist3 = ent1.compoundlist  # type: ignore

    # Copying a CompoundDict
    ent1.compounddict.add('foo')
    ent1.compounddict.add('bar')
    assert static_type_equals(ent1.compounddict['foo'].isubval, int)
    ent1.compounddict['foo'].isubval = 23
    # Copying to the same field on different obj should work.
    ent2.compounddict = ent1.compounddict
    assert ent2.compounddict.keys() == ['foo', 'bar']
    assert ent2.compounddict['foo'].isubval == 23
    # Cross field assigns should work too if the field layouts match..
    ent1.compounddict2 = ent1.compounddict
    # ..And should fail otherwise.
    # (mypy catches this too, but that may not always be the case if
    # two CompoundValues have the same type but different layouts based
    # on their __init__ args or whatnot)
    with pytest.raises(ValueError):
        ent1.compounddict3 = ent1.compounddict  # type: ignore
    # Make sure invalid key types get caught when setting a full dict:
    with pytest.raises(TypeError):
        ent1.compounddict2 = {
            'foo': ent1.compounddict['foo'],
            2: ent1.compounddict['bar'],  # type: ignore
        }


def test_field_access_from_type() -> None:
    """Accessing fields through type objects should return the Field objs."""

    ent = EntityTest()

    # Accessing fields through the type should return field objects
    # instead of values.
    assert static_type_equals(ent.ival, int)
    assert isinstance(ent.ival, int)
    mypytype = 'efro.entity._field.Field[builtins.int*]'
    assert static_type_equals(type(ent).ival, mypytype)
    assert isinstance(type(ent).ival, entity.Field)

    # Accessing subtype on a nested compound field..
    assert static_type_equals(type(ent).compoundlist.d_value, CompoundTest)
    assert isinstance(type(ent).compoundlist.d_value, CompoundTest)


class EntityTestMixin(entity.EntityMixin, CompoundTest2):
    """A test entity created from a compound using a mixin class."""


def test_entity_mixin() -> None:
    """Testing our mixin entity variety."""
    ent = EntityTestMixin()
    assert static_type_equals(ent.isubval2, int)
    assert ent.isubval2 == 3453


def test_entity_embedding() -> None:
    """Making sure compound entities work as expected."""

    class EmbCompoundValTest(entity.CompoundValue):
        """Testing..."""
        isubval = entity.Field('i', entity.IntValue(default=12345))

    class EmbCompoundTest(entity.Entity):
        """Testing..."""
        isubval = entity.Field('i', entity.IntValue(default=12345))
        sub = entity.CompoundField('sub', EmbCompoundValTest())

    # This should be ok...
    _ent = EmbCompoundTest()

    class EmbCompoundValTest2(entity.Entity):
        """Testing..."""
        isubval = entity.Field('i', entity.IntValue(default=12345))

    with pytest.raises(AssertionError):

        # This should not be ok
        # (can only embed CompoundValues, not complete Entities)
        class EmbCompoundTest2(entity.Entity):
            """Testing..."""
            isubval = entity.Field('i', entity.IntValue(default=12345))
            sub = entity.CompoundField('sub', EmbCompoundValTest2())

        _ent2 = EmbCompoundTest2()


def test_key_uniqueness() -> None:
    """Make sure entities reject multiple fields with the same key."""

    # Make sure a single entity with dup keys fails:
    with pytest.raises(RuntimeError):

        class EntityKeyTest(entity.Entity):
            """Test entity with invalid duplicate keys."""
            ival = entity.Field('i', entity.IntValue())
            sval = entity.Field('i', entity.StringValue())

        _ent = EntityKeyTest()

    # Make sure we still get an error if the duplicate keys come from
    # different places in the class hierarchy.
    with pytest.raises(RuntimeError):

        class EntityKeyTest2(entity.Entity):
            """Test entity with invalid duplicate keys."""
            ival = entity.Field('i', entity.IntValue())

        class EntityKeyTest3(EntityKeyTest2):
            """Test entity with invalid duplicate keys."""
            sval = entity.Field('i', entity.StringValue())

        _ent2 = EntityKeyTest3()


def test_data_storage_and_fetching() -> None:
    """Test store_default option for entities."""

    class EntityTestD(entity.Entity):
        """Testing store_default off."""
        ival = entity.Field('i', entity.IntValue(default=3,
                                                 store_default=False))

    class EntityTestD2(entity.Entity):
        """Testing store_default on (the default)."""
        ival = entity.Field('i', entity.IntValue(default=3))

    # This guy should get pruned when its got a default value.
    testd = EntityTestD()
    assert testd.ival == 3
    assert testd.pruned_data() == {}
    testd.ival = 4
    assert testd.pruned_data() == {'i': 4}
    testd.ival = 3
    assert testd.pruned_data() == {}

    # Make sure our pretty/prune json options work.
    assert testd.to_json_str() == '{}'
    assert testd.to_json_str(prune=False) == '{"i":3}'
    assert testd.to_json_str(prune=False, pretty=True) == ('{\n'
                                                           '  "i": 3\n'
                                                           '}')
    # This guy should never get pruned...
    testd2 = EntityTestD2()
    assert testd2.ival == 3
    assert testd2.pruned_data() == {'i': 3}
    testd2.ival = 4
    assert testd2.pruned_data() == {'i': 4}
    testd2.ival = 3
    assert testd2.to_json_str(prune=True) == '{"i":3}'
