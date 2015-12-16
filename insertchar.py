"""Get good matches for unicode code points."""

import collections
import cPickle as pickle
import difflib
import re
import sys

NAMESLIST_FILENAME = 'NamesList.txt'
CACHE_FILENAME = '.cache'


def GetCache():
  try:
    return pickle.load(open(CACHE_FILENAME))
  except IOError:
    return GenerateCache()


def GenerateCache():
  """Generate a cache from NamesList.txt."""
  new_code_point = re.compile(r'^([0-9a-fA-F]{4,})\s+(.*)$')
  alias_line = re.compile(r'^\s*[=%] ([^,]+(?:, )?)+$')
  variation_line = re.compile(
      r'^\s*~ ([0-9a-fA-F]{4,}) ([0-9a-fA-F]{4,}) (.*)$')

  cache = collections.defaultdict(list)

  source = open(NAMESLIST_FILENAME)
  current_point, descriptions = None, []
  for line in source:
    line = line.lower()
    match = new_code_point.match(line)
    if match:
      for desc in descriptions:
        cache[desc].append((current_point,))
      current_point = unichr(int(match.group(1), 16))
      descriptions = [match.group(2)]
    match = alias_line.match(line)
    if match:
      descriptions.extend(match.group(1).split(', '))
    match = variation_line.match(line)
    if match:
      sequence = (unichr(int(match.group(1), 16)),
                  unichr(int(match.group(2), 16)))  # pyformat: disable
      cache[match.group(3)].append(sequence)
  pickle.dump(cache, file(CACHE_FILENAME, 'w'))
  return cache


def main(argv):
  cache = GetCache()
  query = ' '.join(argv[1:]).lower()
  for entry in difflib.get_close_matches(query, cache.iterkeys()):
    print ''.join(cache[entry][0])


if __name__ == '__main__':
  main(sys.argv)
