#
# Crude bit of 2.x python, which screen-scrapes the savage transcript and produces
# a report of what sketches are associated with each WR person found.
#
#

import os
import sys
import string
from HTMLParser import HTMLParser

class MyParser(HTMLParser):
    "A simple parser class."

    def parse(self, s):
        "Parse the given string 's'."
        self.feed(s)
        self.close()
        return self.object

    def __init__(self, verbose=0):
        "Initialise an object, passing 'verbose' to the superclass."
        self.object = None
        self.last_attr_tab = None

        HTMLParser.__init__(self)
        self.hyperlinks = []

    def handle_starttag(self, tag, attrs) :
      if (not self.object) :
        self.object = {}

      attrtab = {}
      self.last_attr_tab = attrtab
      for (attr_name, attr_val) in attrs :
        attrtab[attr_name] = attr_val

      if (not self.object.has_key(tag)) :
        self.object[tag] = []

      self.object[tag].append(attrtab)

    def handle_data(self, data) :
      "Process data."

      if (self.last_attr_tab != None) :
        if (not self.last_attr_tab.has_key("data")) :
          self.last_attr_tab["data"] = []

        self.last_attr_tab["data"].append(data)
      # else :
      #   sys.stderr.write("Dropping data: %s\n" % data)

import urllib, sgmllib

def getPage(name) :
  urlname = name.replace(" ", "_")
  f = urllib.urlopen("http://www.werelate.org/wiki/%s?action=raw" % urlname)
  # print "urlname: {%s}" % urlname
  s = f.read()
  
  if (s) :
    # print s
    myparser = MyParser()
    try:
      pobj = myparser.parse(s)
    except:
      pobj = None
  else:
    print "S NULL 0!!!!"
    pobj = None
  # pobj["url"] = [name]
  return pobj

def getWhatLinksHere(name) :
  specialUrl =  ("http://www.werelate.org/w/index.php?title=Special:Whatlinkshere/Page %s?action=raw" % name)

  urlname = specialUrl.replace(" ", "_")
  f = urllib.urlopen(urlname)
  # f = urllib.urlopen("http://www.werelate.org/wiki/Family:Charlemagne_and_Luitgard,_wife_of_Charlemagne_(1)?action=raw")
  # print "urlname: {%s}" % urlname
  s = f.read()
  
  if (s) :
    # print s
    myparser = MyParser()
    try:
      pobj = myparser.parse(s)
    except:
      pobj = None
  else:
    print "S NULL 1!!!!"
    pobj = None
  # pobj["url"] = [name]
  return pobj

def dumpPage(pobj) :
  for key in pobj.keys() :
    print "\n"
    val = pobj[key]
    print "%s:" % key
    for v in val :
      print "  %s" % v

import re

peopleDict={}
categoryDict={}
sketchCount = 0
sketchPersonCount = 0
seeAlsoCount = 0
oldCategoryPages = []
defectCount = 0

personStringRe=re.compile("Person:[A-Za-z ]+\([0-9]+\)")
sketchDefectRe=re.compile("[Ss]avagetranscriptdefect")
sketchRe=re.compile("[Ss]avagetranscriptsketch")
sketchPersonRe=re.compile("[Ss]avagetranscriptsketch\|\[\[Person:")
seeAlsoRe=re.compile("[Ss]avagepage")
seeAlsoTRe=re.compile("[Ss]avagetranscriptpage")
categoryRe=re.compile("{{[Ss]avagetranscriptcategory\|[^}]*}}")
# [[:Category:The Winthrop Fleet|fleet with Winthrop  1630]]
rawCategoryRe=re.compile("{{:[Cc]ategory:[^|]+\|[^}]+}}")
oldcategoryRe=re.compile("\[[Cc]ategory:.*")
upperCaseChar=re.compile("[A-Z]")
notUpperCaseChar=re.compile("[^A-Z]+")
savageDefectRe=re.compile("{{savagetranscriptdefect\|[0-9]+\|.*}}")

def listOfPersonPages(page, pageText) :
  global sketchCount
  global oldCategoryPages
  listOfPeople=[]
  listFound = personStringRe.findall(pageText)
  oldCategories = oldcategoryRe.findall(pageText)
  if (len(oldCategories) > 0) :
    sys.stdout.write("OLD CATEGORY ON PAGE %s\n" % page)
    oldCategoryPages.append(page)

  # print "listFound: ", str(listFound)
  for foundPerson in listFound :
    if not peopleDict.has_key(foundPerson) :
      peopleDict[foundPerson] = {}

    if not peopleDict[foundPerson].has_key(page) :
      peopleDict[foundPerson][page] = 1
    else :
      peopleDict[foundPerson][page] += 1

def listOfSketches(page, pageText) :
  global peopleDict
  global categoryDict
  global sketchCount
  global sketchPersonCount
  global seeAlsoCount
  global defectCount
  listOfPeople=[]
  sketchesFound = sketchRe.findall(pageText)
  sketchPeopleFound = sketchPersonRe.findall(pageText)
  defectCount = defectCount + len(sketchDefectRe.findall(pageText))

  seeAlsoFound = seeAlsoRe.findall(pageText) + seeAlsoTRe.findall(pageText)
  categoryFound = categoryRe.findall(pageText)
  print "page %s, sketchCount now %d + %d = %d (%d sketch people)" % (page, sketchCount, len(sketchesFound), sketchCount + len(sketchesFound), len(sketchPeopleFound))
  for foundCategory in categoryFound :
    splitCategory = foundCategory.split("|")[1]
    if (not categoryDict.has_key(splitCategory)) :
      categoryDict[splitCategory] = []
    categoryDict[splitCategory].append(page)

  sketchCount = sketchCount + len(sketchesFound)
  sketchPersonCount = sketchPersonCount + len(sketchPeopleFound)
  seeAlsoCount = seeAlsoCount + len(seeAlsoFound)
  # print "listFound: ", str(listFound)
  # for foundPerson in listFound :
  #   if not peopleDict.has_key(foundPerson) :
  #     peopleDict[foundPerson] = {}

  #   if not peopleDict[foundPerson].has_key(page) :
  #     peopleDict[foundPerson][page] = 1
  #   else :
  #     peopleDict[foundPerson][page] += 1

# print s

# Try and process the page.
# The class should have been defined first, remember.
# myparser = MyParser()
# pobj = myparser.parse(s)

def getPerson(name) :
  return getPage("Person:" + name)

def getFamily(name) :
  return getPage("Family:" + name)

def getTranscriptPage(name) :
  tname = "Transcript: " + name

  urlname = tname.replace(" ", "_")
  f = urllib.urlopen("http://www.werelate.org/wiki/%s?action=raw" % urlname)
  # print "urlname: {%s}" % urlname
  s = f.read()
  
  if (s) :
    s.replace("<br>", "\n")
    myparser = MyParser()
    try:
      pobj = myparser.parse(s)
      # print "GOT POBJ"
      lines = []
      if pobj.has_key("to_year") :
        toYearObj = pobj["to_year"]
        toYearData = toYearObj[0]["data"]
        if len(toYearData) > 1 :
          first_lines = []
          for index in range(len(toYearData)) :
            lineObj = {}
            lineObj["data"] = [toYearData[index]]
            if (index < 2) :
              first_lines.append(toYearData[index])
            else :
              lineObj = {}
              lineObj["data"] = [toYearData[index]]
              lines.append(lineObj)
        newToYearObj = {}
        newToYearObj["data"] = first_lines
        pobj["to_year"] = [newToYearObj]
      # print "ABOUT TO CHECK BR PART"
      if pobj.has_key("br") :
        br_lines = pobj["br"]
        pobj["br"] = lines + br_lines

      # print "SAVAGE TRANSCRIPT PAGE AFTER PROCESSING: "
      # dumpPage(pobj)
    except:
      print "SAVAGE PROCESSING BLOWN UP!"
      pobj = None
  else:
    print "S NULL 2!!!!"
    pobj = None
  # pobj["url"] = [name]
  return pobj

def getSavage(page) :
  # sys.stderr.write("DEBUG: getSavage(page = %s)\n" % (page))
  page_file_name = os.path.join("savage_pages", page)

  # if (os.path.isfile(page_file_name)) :
  if (False) :
    # sys.stderr.write("DEBUG: file present!\n")
    fp = open(page_file_name, "r")
    joinedBrLines = fp.read()
    fp.close()

  else :
    # sys.stderr.write("DEBUG: file not found...\n")
    # return getTranscript("Savage%2C James. Genealogical Dictionary of the First Settlers of New England/" + page)
    pObj = getTranscriptPage("Savage, James. Genealogical Dictionary of the First Settlers of New England/" + page)
    joinedBrLines = None
    if (pObj and pObj.has_key("br")) :
      brList = pObj["br"]
      brLines = []
      for lineDict in brList :
        if (lineDict.has_key("data")) :
          brLine = string.join(lineDict["data"])
          # print "lineDict[data] = ", str(lineDict["data"])
          if (brLine.find(")|{{savagetranscript") >= 0) :
            sys.stderr.write("Swapped sense page %s\n" % (str(page)))
          brLines.append(brLine)

      # print "brLines", brLines
      joinedBrLines = " ".join(brLines)
      # print "joinedBrLines", joinedBrLines

      fp = open(page_file_name, "w")
      fp.write(joinedBrLines)
      fp.close()

  return joinedBrLines


currentSketch = None
primary_delimiter = re.compile("{{savagetranscriptsketch|{{savagetranscriptsection")
header_re = re.compile(".*{{savagetranscriptheader.*}}")
category_re = re.compile("\[\[\:Category\:.*\]\]")
see_also_re0 = re.compile("{{savagepage\|[0-9]+\|[0-9]+\|.*}}")
see_also_re1 = re.compile("{{savagetranscriptpage\|[0-9]+\|[0-9]+\|.*}}")
defect_section_re = re.compile("{{savagetranscriptdefect\|[0-9]+\|.*}}")
defect_header_re = re.compile("{{savagetranscriptdefect\|[0-9]+\|")

person_re = re.compile("\[\[Person:[^|]+\|[^\]]+\]\]")
pipe_re = re.compile("\|")
eoln_re = re.compile(r'\n')
# section_continued_re = re.compile("}}.*{{savagetranscriptsectioncontinued\|")
section_continued_re = re.compile("}} *{{savagetranscriptsectioncontinued\|")
sketch_continued_re = re.compile("}} *{{savagetranscriptsketchcontinued\|")
two_close_brackets = re.compile("\]\]")
two_close_braces = re.compile("}}")
section_delimiter = "{{savagetranscriptsection|"
sketch_delimiter = "{{savagetranscriptsketch|"
LEFT_OFFSET = 30
RIGHT_OFFSET = 30
section_dictionary = {}
section_list = []

current_volume = None
current_page = None
current_section = None
current_sketch = None
current_sketch_first_page = None
current_sketch_latest_page = None
current_sketch_content = None


def strip_objects(page, re_obj, strip_method) :
  match_obj = re_obj.search(page)
  count = 0
  finished_text = ""
  while match_obj :
    count = count + 1
    # sys.stdout.write("%d: match_obj.start() = %d, match_obj.end() = %d\n" % (count, match_obj.start(), match_obj.end()))
    replacement = strip_method(page[match_obj.start():match_obj.end()])
    # sys.stdout.write("Found '%s', replacement '%s'\n" % (page[match_obj.start():match_obj.end()], replacement))
    finished_text = finished_text + page[:match_obj.start()] + replacement
    page = page[match_obj.end():]
    # sys.stdout.write("Replacement: continuing with %s\n" % (page))
    match_obj = re_obj.search(page)
    # sys.stdout.write("Subsequent search yields %s\n" % (str(match_obj)))

  return finished_text + page

def strip_header_syntax(matched_string) :
  return ""

def strip_category_syntax(matched_string) :
  last_colon_pos = matched_string.rfind(":")
  if last_colon_pos >= 0 :
    matched_string = matched_string[last_colon_pos:]

  last_bracket_pos = matched_string.find("]")
  if last_bracket_pos >= 0:
    matched_string = matched_string[:last_bracket_pos]

  return matched_string

def strip_seealso_syntax(matched_string) :
  last_pipe_pos = matched_string.rfind("|")
  if last_pipe_pos >= 0 :
    matched_string = matched_string[last_pipe_pos+1:]

  last_brace_pos = matched_string.find("}")
  if last_brace_pos >= 0:
    matched_string = matched_string[:last_brace_pos]

  return matched_string

def strip_person_syntax(matched_person) :
  last_pipe_pos = matched_person.rfind("|")
  if last_pipe_pos >= 0:
    matched_person = matched_person[last_pipe_pos+1:]
  last_bracket_pos = matched_person.find("]")
  if last_bracket_pos >= 0:
    matched_person = matched_person[:last_bracket_pos]
  return matched_person

def strip_section_continued_syntax(matched_syntax) :
  last_pipe_pos = matched_syntax.rfind("|")
  if last_pipe_pos >= 0:
    return " " + matched_syntax[last_pipe_pos+1:]
  else :
    return matched_syntax

def transform_defect_sections(matched_syntax) :
  last_pipe_pos = matched_syntax.rfind("|")
  if last_pipe_pos >= 0:
    return "<s>" + matched_syntax[last_pipe_pos+1:-2] + "</s>"

def obtain_delimiter_name(page) :
  match_obj = two_close_braces.search(page)
  if match_obj:
    name = page[:match_obj.start()]
    match_obj = pipe_re.search(name)
    name = name[match_obj.end():]
    return name
  return None

def trim_name(name) :
  return name.strip().rstrip(" .,")

class Sketch:
  def __init__(self, section, name, volume, first_page, last_page, text) :
    self.section = section

    match_obj = notUpperCaseChar.search(name)

    if match_obj :
      self.prefix = string.strip(name[match_obj.start():match_obj.end()])
      name = name[match_obj.end():]
    else :
      self.prefix = ""

    self.name = name
    self.label = name
    self.volume = volume
    self.first_page = first_page
    self.last_page = last_page
    self.text = text.strip()
    # sys.stderr.write("SKETCH CREATE section=%s, name=%s, volume=%s, first=%s, last=%s, text=%s\n" % (section, name, volume, first_page, last_page, self.text.__repr__()))

  def key(self) :
    return self.section + ":" + self.label

  def vol_and_page_ref(self) :
    if self.first_page == self.last_page :
      return "{{savagepg|" + str(self.volume) + "|" + str(self.first_page) + "}}"
    else :
      return "{{savagepg|" + str(self.volume) + "|" + str(self.first_page) + "}}-{{savagepage|" + str(self.volume) + "|" + str(self.last_page) + "|" + str(self.last_page) + "}}"

      # return str(self.volume) + ":" + str(self.first_page) + "-" + str(self.last_page)

  def wr_people(self) :
    wr_people_re = re.compile("\[\[Person:[^[\]\|]+\|")
    person_dictionary = {}
    for raw_person in wr_people_re.findall(self.text) :
      pipe_pos = pipe_re.search(raw_person)
      person = raw_person[2:pipe_pos.start()]
      person_dictionary[person] = True

    return person_dictionary.keys()

  def quote_for(self, person) :
    def strip_people_except_person(matched_string) :
      if matched_string.startswith("[[" + person + "|") :
        # sys.stdout.write("{%s} -> {%s} NOT CHANGING\n" % (matched_string, matched_string))
        return matched_string
      else :
        pipe_pos = pipe_re.search(matched_string)
        result = matched_string[pipe_pos.start()+1:-2]
        # sys.stdout.write("{%s} -> {%s} CHANGING\n" % (matched_string, result))
        return result

    # Strip away annotation for people other than "person"
    intermediate_text = strip_objects(self.text, person_re, strip_people_except_person)

    # sys.stdout.write("STRIPPED NON ESSENTIAL PEOPLE: {%s}\n" % (intermediate_text))

    def strip_category(matched_syntax) :
      first_pipe_pos = pipe_re.search(matched_syntax)
      if first_pipe_pos :
        second_pipe_pos = pipe_re.search(matched_syntax, first_pipe_pos.start()+1)

        if second_pipe_pos :
          last_pipe_pos = pipe_re.search(matched_syntax, second_pipe_pos.start()+1)

          if last_pipe_pos :
            # return matched_syntax[second_pipe_pos.start()+1:last_pipe_pos.start()]
            return matched_syntax[second_pipe_pos.start()+1:last_pipe_pos.start()]
      return matched_syntax



    stripped_text = strip_objects(intermediate_text, categoryRe, strip_category)
    intermediate_text = stripped_text

    def strip_raw_category(matched_syntax) :
      first_pipe_pos = pipe_re.search(matched_syntax)
      if first_pipe_pos :
        second_pipe_pos = pipe_re.search(matched_syntax, first_pipe_pos.start()+1)

        if second_pipe_pos :
          last_pipe_pos = pipe_re.search(matched_syntax, second_pipe_pos.start()+1)

          if last_pipe_pos :
            result = matched_syntax[second_pipe_pos.start()+1:last_pipe_pos.start()]
            # sys.stderr.write("DEBUG: stripping raw category - matched_syntax = {%s}, returning {%s}\n" % (matched_syntax, result))
            # return matched_syntax[second_pipe_pos.start()+1:last_pipe_pos.start()]
            return result
      return matched_syntax

    # sys.stderr.write("DEBUG: About to search for raw category - intermediate text - {%s}\n" % (intermediate_text))
    sketch_chars = strip_objects(intermediate_text, rawCategoryRe, strip_raw_category)
    # sys.stderr.write("DEBUG: After search for raw category - intermediate text - {%s}\n" % (sketch_chars))

    sketch_types = []
    for i in range(len(sketch_chars)) :
      sketch_types.append(0)

    sketch_chars = stripped_text
    # return stripped_text[:40]

    searchObj = defect_section_re.search(sketch_chars)
    while searchObj :
      sketch_chars_before = sketch_chars[:searchObj.start()]
      sketch_chars_match = sketch_chars[searchObj.start():searchObj.end()]
      sketch_chars_after = sketch_chars[searchObj.end():]
      sketch_types_before = sketch_types[:searchObj.start()]
      sketch_types_match = sketch_types[searchObj.start():searchObj.end()]
      sketch_types_after = sketch_types[searchObj.end():]

      headerMatchObj = defect_header_re.search(sketch_chars_match)
      defectTextStart = headerMatchObj.end()
      defectTextEnd = len(sketch_chars_match)-2
      defect_chars_match = sketch_chars_match[defectTextStart:defectTextEnd]
      defect_types_match = sketch_types[defectTextStart:defectTextEnd]
      for i in range(len(defect_types_match)) :
        defect_types_match[i] = (defect_types_match[i] | 1)

      sketch_chars = sketch_chars_before + defect_chars_match + sketch_chars_after
      sketch_types = sketch_types_before + defect_types_match + sketch_types_after
      if (len(sketch_chars) != len(sketch_types)) :
        sys.stderr.write("DEBUG A: LIST LENGTH DIFFERENT!!\n")
        sys.exit(1)
      searchObj = defect_section_re.search(sketch_chars)

    # return (sketch_chars, sketch_types)
    mperson = person.replace("(", "\\(").replace(")", "\\)")
    header = "\[\[" + mperson + "\|"
    # wr_person_re = re.compile(header + "[^]]+\]\]")
    wr_person_re = re.compile(header + "[^[\[]+\]\]")
    # sys.stderr.write("DEBUG: wr_person_re.pattern = %s\n" % (str(wr_person_re.pattern)))
    searchObj = wr_person_re.search(sketch_chars)

    # sys.stdout.write("      %s\n" % (char_string))
    # sys.stdout.write("      ")
    # for i in range(len(type_string)) :
    #   sys.stdout.write("%s" % (str(type_string[i])))
    # sys.stdout.write("\n")
    if not searchObj :
      sys.stderr.write("DEBUG: NOT FINDING PERSON RECORDED AS PRESENT!\n")
      sys.stderr.write("PERSON: {%s}\n" % (header))
      sys.stderr.write("SKETCH (%d, %d): {%s}\n" % (self.volume, self.first_page, sketch_chars))
    # else :
    #   sys.stderr.write("DEBUG: FOUND PERSON RECORDED AS PRESENT!\n")
    #   sys.stderr.write("PERSON: {%s}\n" % (header))
    #   sys.stderr.write("SKETCH: {%s}\n" % (sketch_chars))
    match_pairs = []
    while searchObj :
      # sys.stderr.write("DEBUG: searchObj.start() = %d, searchObj.end() = %d\n" % (searchObj.start(), searchObj.end()))
      sketch_chars_before = sketch_chars[:searchObj.start()]
      sketch_chars_match = sketch_chars[searchObj.start():searchObj.end()]
      sketch_chars_after = sketch_chars[searchObj.end():]
      # sys.stderr.write("DEBUG: input size = %d\n" % (len(sketch_chars)))
      # sys.stderr.write("DEBUG: char sizes: %d %d %d\n" % (len(sketch_chars_before), len(sketch_chars_match), len(sketch_chars_after)))
      sketch_types_before = sketch_types[:searchObj.start()]
      sketch_types_match = sketch_types[searchObj.start():searchObj.end()]
      sketch_types_after = sketch_types[searchObj.end():]
      # sys.stderr.write("DEBUG: char types: %d %d %d\n" % (len(sketch_types_before), len(sketch_types_match), len(sketch_types_after)))

      sketch_chars_match

      tx_header = re.sub(r"\\", "", header)
      personTextStart = len(tx_header)
      personTextEnd = len(sketch_chars_match)-2

      # sys.stderr.write("DEBUG: sketch_chars_match = %s, personTextStart = %d, personTextEnd = %d\n" % (sketch_chars_match, personTextStart, personTextEnd))
      person_chars_match = sketch_chars_match[personTextStart:personTextEnd]
      person_types_match = sketch_types_match[personTextStart:personTextEnd]
      # sys.stderr.write("DEBUG: person_chars_match = {%s}\n" % (person_chars_match))
      # sys.stderr.write("DEBUG: person_types_match = {%s}\n" % (person_types_match))
      for i in range(len(person_types_match)) :
        person_types_match[i] = (person_types_match[i] | 2)

      match_pairs.append((len(sketch_chars_before), len(sketch_chars_before) + len(person_chars_match)))
      sketch_chars = sketch_chars_before + person_chars_match + sketch_chars_after
      sketch_types = sketch_types_before + person_types_match + sketch_types_after

      if (len(sketch_chars) != len(sketch_types)) :
        sys.stderr.write("DEBUG B: LIST LENGTH DIFFERENT!!\n")
        sys.exit(1)

      searchObj = wr_person_re.search(sketch_chars)

    # sys.stderr.write("DEBUG: initial match_pairs -> %s\n" % (str(match_pairs)))

    for i in range(len(match_pairs)) :
      (begin, end) = match_pairs[i]

      left_offset = LEFT_OFFSET
      right_offset = RIGHT_OFFSET

      if (begin < left_offset) :
        right_offset = right_offset + (left_offset - begin)

      elif ((end + RIGHT_OFFSET) > (len(sketch_chars))) :
        left_offset = left_offset + ((end + RIGHT_OFFSET) - len(sketch_chars))

      if (begin > left_offset) :
        new_begin = begin - left_offset
      else :
        new_begin = 0

      # Move further back until we hit a space...
      while ((new_begin > 0) and (sketch_chars[new_begin] != " ")) :
        new_begin = new_begin - 1

      if ((end + right_offset) > (len(sketch_chars))) :
        new_end = len(sketch_chars)
      else :
        new_end = end + right_offset

      # Move further forward until we hit a space...
      while ((new_end < len(sketch_chars)) and (sketch_chars[new_end] != " ")) :
        new_end = new_end + 1

      match_pairs[i] = (new_begin, new_end)

    # sys.stderr.write("DEBUG: expanded match_pairs -> %s\n" % (str(match_pairs)))

    i = 0
    while i < (len(match_pairs) - 1) :
      (first_pair_begin, first_pair_end) = match_pairs[i]
      (next_pair_begin, next_pair_end) = match_pairs[i+1]
      # If current pair overlaps next pair - or it's so close that the
      # elipses would take as much space as the content - then join them
      if ((first_pair_end + 3) >= next_pair_begin) :
        match_pairs[i] = (first_pair_begin, next_pair_end)
        del match_pairs[i+1]
        # sys.stderr.write("DEBUG: CONSOLIDATING TWO MATCH PAIRS!!!\n")
      else :
        i = i + 1

    # sys.stdout.write("DEBUG: consolidated match_pairs -> %s\n" % (str(match_pairs)))

    result_str = ""
    # sys.stdout.write("len(match_pairs) = %d\n" % (len(match_pairs)))
    # sys.stdout.write("match_pairs[0] = %s\n" % (str(match_pairs[0])))
    # sys.stdout.write("match_pairs[0][0] = %s\n" % (str(match_pairs[0][0])))
    if (match_pairs[0][0] > 0) :
      result_str = "..."
    else :
      result_str = ""

    for i in range(len(match_pairs)) :
      (pair_begin, pair_end) = match_pairs[i]
      if (i == 0) :
        if (pair_begin > 0) :
          result_str = "..."
        else :
          result_str = ""
      else :
        result_str = result_str + " ..."

      # sys.stdout.write("DEBUG: pair_begin = %s\n" % (str(pair_begin)))
      # sys.stdout.write("DEBUG: pair_end = %s\n" % (str(pair_end)))

      section = ""
      # Obtain section of sketch_chars from pair_begin to pair_end, insert appropriate <del> and </del> where needed
      active_char_type = 0
      for j in range(pair_begin, pair_end) :
        # Transition from active_char_type to what we find in sketch_types[j] :
        transition = (((active_char_type & 0x03) << 4) | (sketch_types[j] & 0x03))
        # sys.stdout.write("Transition = 0x%04x\n" % (transition))
        active_char_type = sketch_types[j]

        if   transition == 0x00 :
          transition_str = ""

        elif transition == 0x01 :
          transition_str = "<del>"

        elif transition == 0x02 :
          transition_str = "'''"

        elif transition == 0x03 :
          transition_str = "<del>'''"

        elif transition == 0x10 :
          transition_str = "</del>"

        elif transition == 0x11 :
          transition_str = ""
        elif transition == 0x12 :
          transition_str = "</del>'''"

        elif transition == 0x13 :
          transition_str = "'''"

        elif transition == 0x20 :
          transition_str = "'''"

        elif transition == 0x21 :
          transition_str = "'''<del>"

        elif transition == 0x22 :
          transition_str = ""

        elif transition == 0x23 :
          transition_str = "<del>"

        elif transition == 0x30 :
          transition_str = "'''</del>"

        elif transition == 0x31 :
          transition_str = "'''"

        elif transition == 0x32 :
          transition_str = "</del>"

        elif transition == 0x33 :
          transition_str = ""

        section = section + transition_str + sketch_chars[j]

      if active_char_type == 0x1 :
        section = section + "</del>"

      elif active_char_type == 0x2 :
        section = section + "'''"

      elif active_char_type == 0x3 :
        section = section + "'''</del>"

      result_str = result_str + " " + string.strip(section)

    if pair_end < len(sketch_chars) :
      result_str = result_str + " ..."

    return result_str

def process_page(page=None, v=0, p=0) :
  global current_section
  global current_sketch
  global current_sketch_content
  global current_volume
  global current_page

  if page == None:
    return

  current_volume = v
  current_page = p

  # Strip header line...
  page = strip_objects(page, header_re, strip_header_syntax)

  # Strip away category stuff
  page = strip_objects(page, category_re, strip_category_syntax)

  # Strip away see also (first type) stuff
  page = strip_objects(page, see_also_re0, strip_seealso_syntax)

  # Strip away see also (second type) stuff
  page = strip_objects(page, see_also_re1, strip_seealso_syntax)

  # Strip away eoln characters
  lpage = list(page)
  for index in range(len(lpage)) :
    if ord(lpage[index]) == 10 :
      lpage[index] = ' '
  page = ''.join(lpage)

  # Strip away section continued stuff
  page = strip_objects(page, section_continued_re, strip_section_continued_syntax)

  # Strip away sketch continued stuff
  page = strip_objects(page, sketch_continued_re, strip_section_continued_syntax)

  def consume_page_content(page, index) :
    global current_sketch_content
    global current_sketch_latest_page

    if current_sketch != None :
      current_sketch_latest_page = current_page
      current_sketch_content = current_sketch_content + page[:index]
    return page[index:]

  def finish_current_sketch() :
    global current_sketch
    global current_sketch_content

    if current_sketch == None :
      return

    # sys.stderr.write("DEBUG: Completed sketch {\"%s\", \"%s\"} page %s to %s\n" % (current_section, current_sketch, current_sketch_first_page, current_sketch_latest_page))
    if (not section_dictionary.has_key(current_section)) :
      section_dictionary[current_section] = []
      section_list.append(current_section)
    sketch = Sketch(current_section, current_sketch, current_volume, current_sketch_first_page, current_sketch_latest_page, \
                    current_sketch_content)
    section_dictionary[current_section].append(sketch)

    current_sketch = None
    current_sketch_content = None


  def process_new_section(page) :
    global current_section
    # sys.stderr.write("PROCESS NEW SECTION ENTRY...\n")
    finish_current_sketch()
    # sys.stderr.write("PROCESS NEW SECTION PAST FINISH OF SKETCH...\n")

    current_section = trim_name(obtain_delimiter_name(page))
    # sys.stderr.write("NEW SECTION IS %s\n" % (str(current_section)))

    close_braces_match = two_close_braces.search(page)
    if close_braces_match :
      return page[close_braces_match.end():]
    else :
      return page

  def process_new_sketch(page) :
    global current_sketch
    global current_sketch_content
    global current_sketch_first_page

    finish_current_sketch()
    raw_name = obtain_delimiter_name(page)
    current_sketch = trim_name(strip_objects(raw_name, person_re, strip_person_syntax))
    current_sketch_first_page = current_page
    current_sketch_latest_page = current_page
    current_sketch_content = raw_name

    close_braces_match = two_close_braces.search(page)
    if close_braces_match :
      return page[close_braces_match.end():]
    else :
      return page



  while len(page) > 0 :
    delim_match = primary_delimiter.search(page)

    if delim_match:
      page = consume_page_content(page, delim_match.start())

      if page[:len(section_delimiter)] == section_delimiter :
        page = process_new_section(page)

      elif page[:len(sketch_delimiter)] == sketch_delimiter :
        page = process_new_sketch(page)

      else :
        page = consume_page_content(page, delim_match.end())

    else :
      page = consume_page_content(page, len(page))

      page = ""
      break

  # print page

  return

  chunks = page.split("{{savagetranscriptsketch|")
  for item in chunks :
    print "CHUNK: %s" % (item)



sketch_by_key = {}
sketches_by_person = {}


for v in [1, 2, 3, 4] :
  for p in range(1, 700) :
     page = ("v%dp%d" % (v, p))
     pageText = getSavage(page)
     if pageText == None:
       break
     process_page(pageText, v, p)

  process_page()

for section in section_list :
    label_counts = {}
    sketch_list = section_dictionary[section]

    for sketch in sketch_list :
      if not label_counts.has_key(sketch.name) :
        label_counts[sketch.name] = 1
      else :
        label_counts[sketch.name] = label_counts[sketch.name] + 1

    name_counts = {}
    for sketch in sketch_list :
      total_count = label_counts[sketch.name]
      if (name_counts.has_key(sketch.name)) :
        how_many_this_name = name_counts[sketch.name] + 1
      else :
        how_many_this_name = 1
      name_counts[sketch.name] = how_many_this_name

      if total_count > 1 :
        sketch.label = sketch.name + " " + str(how_many_this_name) + " of " + str(total_count)
      # sys.stderr.write("DEBUG (%s:%s): Sketch Label %s\n" % (str(sketch.volume), str(sketch.first_page), sketch.label))

for section in section_list :
    # sys.stderr.write("SECTION %s:\n" % (section))
    sketch_list = section_dictionary[section]
    for sketch in sketch_list :
      # sys.stderr.write("    %s, %s, %s-%s\n" % (sketch.label, sketch.volume, sketch.first_page, sketch.last_page))
      # strike_start = sketch.text.find("<s>")
      # if strike_start >= 0 :
      #   sys.stderr.write("      DEFECTIVE SKETCH: %s\n" % (sketch.text))
      # else :
      #   sys.stderr.write("      FAIR SKETCH:      %s\n" % (sketch.text))

      # sys.stderr.write("          PEOPLE:       %s\n" % (sketch.wr_people()))

      sketch_by_key[sketch.key()] = sketch

      for person in sketch.wr_people() :
        if not sketches_by_person.has_key(person) :
          sketches_by_person[person] = [sketch.key()]
        else :
          sketch_list = sketches_by_person[person]
          if not sketch.key() in sketch_list :
            sketches_by_person[person].append(sketch.key())


import time
# sys.stderr.write("SLEEPING.....\n")
# time.sleep(10)

sort_list = []
num_suffix = re.compile("\([0-9]+\)$")
for person in sketches_by_person.keys() :

  if (not person.startswith("Person:")) :
    continue
  intermediate_person = person[7:]

  num_match = num_suffix.search(intermediate_person)
  if not num_match:
    continue

  stripped_person = string.strip(intermediate_person[:num_match.start()])
  parts = stripped_person.split(" ", 1)

  if (len(parts) != 2) :
    sys.stdout.write("Split(\"%s\") = %s\n" % (person, parts.__repr__()))
  else :
    first = parts[0]
    last = parts[1]
    # sequence = person[num_match.start(), num_match.finish()]
    sequence = intermediate_person[num_match.start():num_match.end()]

  seq_num = int(sequence[1:-1])
  if (last == "Unknown") :
    last = "ZZZZZZZZZZ"
  if (first == "Unknown") :
    first = "ZZZZZZZZZZ"
  sort_list.append((last.upper(), first.upper(), seq_num, person))

sys.stderr.write("Sort list created, length %d\n" % (len(sort_list)))
sort_list.sort()
sys.stderr.write("Sorted list created, length %d\n" % (len(sort_list)))

sorted_names = []
for index in range(len(sort_list)) :
  (last, first, seq_num, person) = sort_list[index]
  sorted_names.append(person)

limit = 300000

name_list = sorted_names

# for person in sketches_by_person.keys() :
for person in name_list :
  if limit <= 0: break
  limit = limit - 1
  sys.stdout.write("[[" + person + "]]\n")
  for sketch_key in sketches_by_person[person] :
    sketch = sketch_by_key[sketch_key]

    # sys.stdout.write("  %s; %s; \"%s\"\n" % (sketch.vol_and_page_ref(), sketch_key, sketch.quote_for(person)))
    rsketch_key = sketch_key.replace(":", "; ")
    result_str = sketch.quote_for(person)
    sys.stdout.write("  %s; %s; %s<br>\n" % (sketch.vol_and_page_ref(), rsketch_key, result_str))

  sys.stdout.write("<br>\n")

