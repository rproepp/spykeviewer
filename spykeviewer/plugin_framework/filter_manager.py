import re
import codecs
from collections import OrderedDict

def _move_ordered_dict_item(o_dict, item_key, new_position):
    """ Move an item in an ordered dictionary to a new position
        :Parameters:
            o_dict : OrderedDict
                The dictionary on which the move takes place
            item_key : key
                The key of the item to move. If the key does not exist in
                the dictionary, this function will do nothing.
            new_position : key
                The item to move will be inserted after the item with this
                key. If this key does not exist in the dictionary, the item
                will be moved to the first position.
    """
    # Bad performance, use only on small dictionaries
    # and/or non time-critical places
    if not o_dict or not item_key in o_dict:
        return

    item = o_dict[item_key]
    items = o_dict.items()
    in_there = new_position in o_dict

    o_dict.clear()
    if not in_there:
        o_dict[item_key] = item

    for i in items:
        if i[0] != item_key:
            o_dict[i[0]] = i[1]
        if i[0] == new_position:
            o_dict[item_key] = item

class FilterManager:
    """ Manage custom filters for NEO object selection
    """

    class Filter:
        """ Represents a single filter
        """
        def __init__(self, code, parent, active=True, on_exception=True):
            """ Creates a new filter
                :Parameters:
                    code : list
                        List of lines of code in the filter function
                    active : bool
                        Is the filter active?
                    on_exception : bool
                        Should the filter return True on an exception?
            """
            self.code = code
            self.active = active
            self.on_exception = on_exception
            self._parent = parent

        def function(self):
            return self._parent._get_filter_function(self)

    class FilterGroup:
        """ Represents either a filter group
        """
        def __init__(self, exclusive=False):
            self.filters = OrderedDict()
            self.exclusive = exclusive

        def list_items(self):
            """ Returns a list of (name, filter) tuples
            """
            return self.filters.items()

        def move_filter(self, item, new_pos):
            """ Move an item to a new position
                :Parameters:
                item : str
                    The key of the item to move. If the key does not exist,
                    this method will do nothing.
                new_position : str
                    The item to move will be inserted after the item with
                    this key. If this key does not exist, the item will be
                    moved to the first position.
            """
            _move_ordered_dict_item(self.filters, item, new_pos)

    def __init__(self, parameter_list, filename):
        """ Constructs filter object with a given method parameter list
            (given as string) and filename
        """
        self.signature = parameter_list
        self.filename = filename
        self.filters = OrderedDict()
        self.currently_loading = False

        try:
            self.load()
        except IOError:
            pass

    def _load_filter_group(self, s, group):
        # Work regular expression magic to extract method names and code
        s = s.replace('    ', '\t')
        nl = '(?:\n|\r|\r\n)' # Different possibilities for newline
        it = re.finditer('^def filter\\(%s\\):(?P<flags>\s*#.*)?%s\t"""(?P<name>[^"]*)"""%s(?P<body>(?:\t.*%s)*)'
            % (self.signature, nl,nl,nl), s, re.M)
        for i in it:
            name = i.group('name')
            # Remove starting tabs
            body = [x[1:] for x in re.split(nl, i.group('body'))]
            if body[-1] == '':
                body = body[:-1]

            flag_string = i.group('flags')
            active = False
            on_exception = False
            if flag_string:
                flags = flag_string.strip()[1:].split(',')
                for f in flags:
                    f = f.strip()
                    if f == 'ACTIVE':
                        active = True
                    elif f == 'EXCEPTION_TRUE':
                        on_exception = True
            self.add_filter(name, body, active, on_exception, group)

    def load(self):
        """ Clears all filters and reloads them from file
        """
        self.currently_loading = True
        f = codecs.open(self.filename, 'r', 'utf-8')
        s = f.read()
        # Search for groups and load filters for each group
        start = 0
        end = 0
        while end >= 0:
            group_pos = s.find('#GROUP ', start)
            if group_pos >= 0:
                self._load_filter_group(s[start:group_pos], None)

                lines = s[group_pos:].splitlines()
                group = lines[0][7:]
                self.add_group(group, lines[1].strip() == '#EXCLUSIVE')

                end = s.find('#ENDGROUP', group_pos)
                if end >= 0:
                    self._load_filter_group(s[group_pos:end], group)
                else:
                    self._load_filter_group(s[group_pos:], group)
                start = end
            else:
                end = group_pos

        if start >= 0:
            self._load_filter_group(s[start:], None)

        f.close()
        self.currently_loading = False

    def _write_filter(self, file, name, flt):
        file.write('\ndef filter(%s):' % self.signature)
        if flt.active or flt.on_exception:
            file.write(' #')
            if flt.active:
                file.write('ACTIVE')
                if flt.on_exception:
                    file.write(',')
            if flt.on_exception:
                file.write('EXCEPTION_TRUE')
        file.write('\n')

        file.write('\t"""%s"""\n' % name)
        for l in flt.code:
            file.write('\t%s\n' % l)

    def save(self):
        """ Saves all filters to file
        """
        f = codecs.open(self.filename, 'w', 'utf-8')
        f.write('# Filter file. All functions need to have the same parameter list.\n')
        f.write('# All code outside of functions (e.g. imports) will be ignored!\n')
        f.write('# When editing this file manually, use tab indentation or indent by 4 spaces,\n')
        f.write('# otherwise the filter functions will not be recognized!\n')
        for n,i in self.filters.iteritems():
            if isinstance(i, self.FilterGroup):
                f.write('\n#GROUP %s\n' % n)
                if i.exclusive:
                    f.write('#EXCLUSIVE\n')
                for fn, flt in i.filters.iteritems():
                    self._write_filter(f, fn, flt)
                f.write('#ENDGROUP\n')
            else:
                self._write_filter(f, n, i)
        f.close()

    def add_item(self, item, name, group_name=None, overwrite=False):
        """ Adds an existing item (Filter or FilterGroup)
            :Parameters:
                name : str
                    Name of the new filter
                item : Filter or FilterGroup
                    The item to add
                group_name : str
                    Name of the group that the new filter belongs to. If this
                    is None, the filter will not belong to any groop (root level)
                    Default: None
                overwrite : bool
                    If true, an existing item with the same name will be
                    overwritten. If false and an item with the same name
                    exists, a value error is raised.
                    Default : False
        """
        if not group_name:
            if name in self.filters:
                if not overwrite:
                    raise ValueError('A filter or filter group named "%s" already exists!' % str(name))
                prev = self.filters[name]
                if isinstance(prev, FilterManager.FilterGroup) \
                    and isinstance(item, FilterManager.Filter):
                    raise ValueError('A filter group named "%s" already exists!' % str(name))
                if isinstance(prev, FilterManager.Filter) \
                    and isinstance(item, FilterManager.FilterGroup):
                    raise ValueError('A filter named "%s" already exists!' % str(name))

            self.filters[name] = item
        else:
            if not group_name in self.filters:
                raise ValueError('No filter group named "%s" exists!' % str(group_name))
            g = self.filters[group_name]
            if overwrite and name in g.filters:
                raise ValueError('A filter named "%s" already exists in group "%s"!' % (str(name), str(group_name)))
            if g.exclusive and not self.currently_loading:
                if any(f.active for f in g.filters.itervalues()):
                    item.active = False
                elif all(not f.active for f in g.filters.itervalues()):
                    item.active = True
            g.filters[name] = item

    def add_group(self, name, exclusive, group_filters=None, overwrite=False):
        """ Adds a filter group
            :Parameters:
                name : str
                    Name of the new filter
                exclusive : bool
                    Determines if only one item in the group can be active
                group_filters : OrderedDict
                    An ordered dictionary, indexed by name, of filters
                    belonging to the group
                overwrite : bool
                    If true, an existing group with the same name will be
                    overwritten. If false and a group with the same name
                    exists, a value error is raised.
                    Default : False
        """
        if name in self.filters:
            prev = self.filters[name]
            if isinstance(prev, FilterManager.Filter):
                raise ValueError('A filter with this name already exists!')
            if not overwrite:
                raise ValueError('A filter group with this name already exists!')
        g = self.FilterGroup(exclusive)
        g.filters = group_filters if group_filters else OrderedDict()
        self.filters[name] = g

    def add_filter(self, name, code, active=True, on_exception=True, group_name=None, overwrite=False):
        """ Adds a filter
            :Parameters:
                name : str
                    Name of the new filter
                code : list
                    List of lines of code in the filter function
                active : bool
                    Is the filter active?
                    Default: True
                on_exception : bool
                    Should the filter return True on an exception?
                    Default: True
                group_name : str
                    Name of the group that the new filter belongs to. If this is None, the filter will not
                    belong to any groop (root level)
                    Default: None
                overwrite : bool
                    If true, an existing filter with the same name will be
                    overwritten. If false and a filter with the same name
                    exists, a value error is raised.
                    Default : False
        """
        self.add_item(self.Filter(code, self, active, on_exception), name, group_name, overwrite)

    def get_item(self, name, group=None):
        """ Returns a filter or filter group object
            :Parameters:
                item : str
                    Name of the selected filter or filter group
                group : str
                    Name of the group to which the filter belongs. Only
                    valid for filter objects, not for filter groups.
                    If this is None, a top level item is used.
                    Default: None
            :Returns:
                FilterManager.Filter : The filter object
        """
        if not group:
            if not name in self.filters:
                raise KeyError('No item named "%s" exists!' % str(name))
            return self.filters[name]
        else:
            if not group in self.filters:
                raise KeyError('No group named "%s" exists!' % str(group))

            g = self.filters[group]
            if not isinstance(g, self.FilterGroup):
                raise TypeError('Item "%s" is not a filter group!' % str(group))
            if not name in g.filters:
                raise KeyError('No item named "%s" exists!' % str(name))
            return g.filters[name]

    def get_group_filters(self, group):
        if not group in self.filters:
            raise KeyError('No item named "%s" exists!' % str(group))
        g = self.filters[group]
        if not isinstance(g, self.FilterGroup):
            raise TypeError('Item "%s" is not a filter group!' % str(group))

        return g.filters

    def _get_filter_function(self, filter):
        local = {}
        s = 'def fun(%s):\n\t' % self.signature
        s += '\n\t'.join(filter.code)
        exec(s,{},local)
        return local['fun']

    def list_items(self):
        """ Returns a list of (name, filter/FilterManager.FilterGroup) tuples
        """
        return self.filters.items()

    def move_item(self, item, new_pos, group_name=None):
        """ Move an item to a new position
            :Parameters:
            item_key : key
                The key of the item to move. If the key does not exist,
                this method will do nothing.
            new_position : key
                The item to move will be inserted after the item with this key.
                 If this key does not exist, the item will be moved to the first position.
        """
        if not group_name:
            _move_ordered_dict_item(self.filters, item, new_pos)
        else:
            self.filters[group_name].move_filter(item, new_pos)

    def get_active_filters(self):
        """ Returns a list of all active filters contained in this manager
        """
        ret = []
        for i in self.filters.values():
            if isinstance(i, self.FilterGroup):
                for f in i.filters.values():
                    if f.active:
                        ret.append(f)
            else:
                if i.active:
                    ret.append(i)
        return ret

    def list_group_names(self):
        """ Returns a list of names of filter groups
        """
        names = []
        for n, i in self.filters.iteritems():
            if isinstance(i, self.FilterGroup):
                names.append(n)
        return names

    def remove_item(self, item, group=None):
        """ Removes an item from the filter tree
            :Parameters:
                item : str
                    Name of the item to be removed
                group : str
                    Name of the group to which the item belongs. If this is
                    None, a top level item will be removed
                    Default: None
        """
        if not group:
            if not item in self.filters:
                raise KeyError('No item named "%s" exists!' % str(item))
            self.filters.pop(item)
        else:
            if not group in self.filters:
                raise KeyError('No group named "%s" exists!' % str(group))

            g = self.filters[group]
            if not isinstance(g, self.FilterGroup):
                raise TypeError('Item "%s" is not a filter group!' % str(group))
            if not item in g.filters:
                raise KeyError('No item named "%s" exists!' % str(item))
            g.filters.pop(item)

    def group_exclusive(self, name):
        """ Returns if a group is exclusvie
        """
        if not name in self.filters or not isinstance(self.filters[name], self.FilterGroup):
            return False
        return self.filters[name].exclusive