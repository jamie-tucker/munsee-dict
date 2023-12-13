from munseedict import utils
import Levenshtein

#region General

dictionary = utils.get_csv("dictionary.csv")

# Clean database
# remove aliases for the Entry and only use the main version for etymological parsing
"""
Processes a string with square brackets, returning variants with and without the content inside the brackets.
ato[h] -> ato;atoh , -[w]aakan = -aakan;-waakan , alangweew -> alangweew
"""
def process_bracketed_string(input_str):
  start, end = input_str.find('['), input_str.find(']')
  if start != -1 and end != -1:
    before, inside, after = input_str[:start], input_str[start + 1:end], input_str[end + 1:]
    return f"{before}{after};{before}{inside}{after}"
  return input_str

# ato;atoh becomes ato
# -ush becomes ush
def remove_aliases(input_str):
  result = ""
  if ';' in input_str:
      result = input_str.split(';')[0]
  result = input_str.replace('-', '')
  return result

'''
# Create a new column to store the original entries
data['Original_Entry'] = data['Entry']
# Apply the process_entries function to the "Entry" column
data['Entry'] = data['Entry'].apply(process_bracketed_string)
# Now data contains both the processed entries and the original entries
# Save the DataFrame with processed entries to a new CSV file
data.to_csv('processed_dictionary.csv', index=False)
# To revert to the original entries, you can do the following:
data['Entry'] = data['Original_Entry']
# Save the DataFrame with original entries to another CSV file
data.to_csv('your_reverted_file.csv', index=False)
'''

def is_consonant(c):
  return c.isalpha() and c.lower() not in 'aeiou'

def is_vowel(c):
  return c.isalpha() and c.lower() in 'aeiou'

def trim_final_vowels(word):
  while (is_vowel(word[-1])): word = word[:-1]
  return word

def trim_initial_vowels(word):
  while (is_vowel(word[0])): word = word[1:]
  return word


def find_closest_entry(word, pos):
  # Filter entries based on POS
  pos_entries = dictionary[dictionary['POS'].str.contains(pos, na=False)]
  # Use edit distance to find the closest word
  closest_entry = min(pos_entries['Entry'], key=lambda x: Levenshtein.distance(x, word))
  return closest_entry

# Define replacements as a global variable
replacements = {
  "ch": "č",
  "sh": "š",
  "zh": "ž",
  "aa": "ā",
  "ee": "ē",
  "ii": "ī",
  "oo": "ō"
}

# munseeToEnglish
def mte(input_str):
  output_str = input_str
  for key, value in replacements.items():
    output_str = output_str.replace(key, value)
  return output_str

# englishToMunsee
def etm(input_str):
  # Create reverse replacements by swapping keys and values
  reverse_replacements = {value: key for key, value in replacements.items()}
  output_str = input_str
  for key, value in reverse_replacements.items():
    output_str = output_str.replace(key, value)
  return output_str

def find_closest_entry(word, pos):
  # Filter entries based on POS
  pos_entries = dictionary[dictionary['POS'].str.contains(pos, na=False)]
  # Use edit distance to find the closest word, applying etm function first
  closest_entry = min(pos_entries['Entry'], key=lambda x: Levenshtein.distance(etm(x.replace('*', '')), etm(word)))
  return closest_entry

def prefix_edit_distance(str1, str2):
  # Calculate the Levenshtein distance only for the prefix
  min_len = min(len(str1), len(str2))
  prefix_distance = Levenshtein.distance(str1[:min_len], str2[:min_len])
  return prefix_distance

# parts of speech that correspond to standalone words, not parts of words such as prefixes, medials, suffixes
# all parts of speech listed in O'Meara's Delaware Dictionary except pv & pn (preverb and prenoun)
noun_pos = ['na', 'ni', 'nad', 'nid']
verb_pos = ['vai', 'vai-s', 'vii', 'vii-s', 'vta', 'vti1a', 'vti1b', 'vti2', 'vti3', 'vtao', 'vaio', 'voti']
particle_pos = ['pc', 'pr']
word_pos = noun_pos + verb_pos + particle_pos

nonword_noun_pos = ["np", "nb", "nmed", "npom", "nfin"]
nonword_verb_pos = ["vp", "vinc", "vmed", "vpf", "vf", "vpos", "vts"]
nonword_pos = nonword_noun_pos + nonword_verb_pos

pos_tagset = word_pos + nonword_pos

#endregion

#region Nouns

def check_reduplication(word, pos):
  #ex: pehpetahkuw, there is a lot of thunder
  if len(word) >= 4:
    if word[0] == word[3] and is_consonant(word[0]):
      if is_vowel(word[1]) and word[2] == 'h':
        return "reduplication:"+word
  if len(word) >= 3:
    if word[0] == word[2] and is_consonant(word[0]) and is_vowel(word[1]):
      return "reduplication:"+word
    if word.startswith("a") and word[0] == word[2]:
      return "reduplication:"+word

def check_diminutive(word, pos):
  if word.endswith("s"):
    root = find_closest_entry(trim_final_vowels(word[:-1]), pos)
    suffix = "+-us"
    word = root+suffix
    return word
  elif word.endswith("sh"):
    root = find_closest_entry(trim_final_vowels(word[:-2]), pos)
    suffix = "+-ush"
    word = root+suffix
    return word

def check_locative(word, pos):
  if word.endswith("ng"):
    root = find_closest_entry(trim_final_vowels(word[:-2]), pos)
    suffix = "+-ung"
    return root+suffix

def check_plural(word, pos):
  if word.endswith("ak") or word.endswith("al"):
    root = find_closest_entry(trim_final_vowels(word[:-2]), pos)
    suffix = "+-" + word[-2:]
    word = root+suffix
    return word

def check_prenoun(word, pos):
  prenouns = dictionary[dictionary['POS'].str.contains('np', na=False)]
  for index, row in prenouns.iterrows():
    prenoun = row['Entry']
    prefix = prenoun.replace('-', '')
    if word.startswith(prefix):
      root = find_closest_entry(word[len(prefix):], 'n')
      word = prenoun + "+" + root
      return word
    else:
      prefix = trim_final_vowels(prenoun.replace('-', ''))
      if word.startswith(prefix):
        root = find_closest_entry(word[len(prefix):], 'n')
        word = prenoun + "+" + root
        return word

def check_nfin(word, pos):
  '''
  nfins = dictionary[dictionary['POS'].str.contains('nfin', na=False)]
  for index, row in nfins.iterrows():
    noun_final = row['Entry']
    suffix = noun_final.replace('-', '')
    if word.endswith(suffix):
      root = find_closest_entry(word[len(suffix):], 'v') #verb_pos
      word = root + "+" + noun_final
      return word
    else:
      suffix = trim_initial_vowels(noun_final.replace('-', ''))
      if word.endswith(suffix):
        root = find_closest_entry(word[len(suffix):], 'v')
        word = root + "+" + noun_final
        return word
  '''
  nfins = dictionary[dictionary['POS'].str.contains('nfin', na=False)]
  best_match = None
  min_distance = float('inf')

  for index, row in nfins.iterrows():
    noun_final = row['Entry']
    suffix = noun_final.replace('-', '')

    # Calculate edit distance for the suffix
    distance = Levenshtein.distance(word[-len(suffix):], suffix)
    # If the current suffix is a better match, update the best_match
    if distance < min_distance:
      min_distance = distance
      best_match = noun_final

    # Also check with trimmed initial vowels
    suffix = trim_initial_vowels(noun_final.replace('-', ''))
    distance = Levenshtein.distance(word[-len(suffix):], suffix)
    if distance < min_distance:
      min_distance = distance
      best_match = noun_final

    if best_match:
      root = find_closest_entry(word[:-len(best_match)], 'v')
      word = root + "+" + best_match
      return word

#endregion

#region Verbs

# approximate the underlying form of a verb given its lemma form and POS
# maxkeew -> maxk
def findVerbStem(verb, pos):
  root = verb

  if(pos == "vta"):
    root = verb[:-3] # remove eew from 3rd person inflected form

  match pos:
    # vai
    case "vai" if(root.endswith("suw")): # /-usii/  What about "wiisuw" which is /-ii/ not /-usii/
      return root[:-3]
    case "vai" if(root.endswith("uw")): # /-ii/ unstable
      return root[:-2]
    case "vai" if(root.endswith("ul")): # /-ul/
      return root[:-2]
    case "vai" if(root.endswith("iil")):  # /-ul/
      return root[:-1]
    case "vai" if(root.endswith("xiin")): # /-iin/
      return root[:-3]
    case "vai" if(root.endswith("aam")): # /-aam/ 'sleep'
      return root
    case "vai" if(root.endswith("hl")): # /-hl/ 'motion'
      return root
    case "vai" if(root.endswith("keew")): # /-kaa/ or /-kee/ 'dance'
      return root[:-1]
    case "vai" if(root.endswith("pahtoow")): # /-pahtoo/ 'hurry, run'
      return root[:-1]
    case "vai" if(root.endswith("eew")): # /-ee/ or /-aa/ unstable
      return root[:-3]
    case "vai":
      print(f"{verb!r} has an unrecognized {pos!r} final")

    case "vai-s" if(root.endswith("iiw")): # /-ii/ stable
      return root[:-3]
    case "vai-s" if(root.endswith("aaw")): # /-aa/ stable
      return root[:-3]
    case "vai-s":
      print(f"{verb!r} has and unrecognized {pos!r} final")

    # vii
    case "vii" if(root.endswith("eew")):
      return root[:-3]
    case "vii" if(root.endswith("aaw")):
      return root[:-3]
    case "vii" if(root.endswith("iiw")):
      return root[:-3]
    case "vii" if(root.endswith("at")):
      return root[:-2]
    case "vii" if(root.endwith("uw")):
      return root[:-2]
    case "vii" if(root.endswith("an")):
      return root[:-2]
    case "vii" if(root.endswith("un")):
      return root[:-2]
    case "vii" if(root.endswith("unool")): # /-un-/ + /-al/
      return root[:-5]
    case "vii" if(root.endswith("ut")):
      return root[:-2]
    case "vii" if(root.endswith("tool")):
      return root[:-4]
    case "vii":
      print(f"{verb!r} has an unrecognized {pos!r} final")

    # vta
    case "vta" if(root.endswith("aw")):
      return root[:-2]
    case "vta" if(root.endswith("w")):
      return root[:-1]
    case "vta" if(root.endswith("l")):
      return root[:-1]
    case "vta":
      return root

    # vti
    case "vti1a" if(root.endswith("am")):
      return root[:-2]
    case "vti1a":
      print(f"{verb!r} has an unrecognized {pos!r} final")
    case "vti1b" if(root.endswith("um")):
      return root[:-2]
    case "vti1b":
      print(f"{verb!r} has an unrecognized {pos!r} final")
    case "vti2" if(root.endswith("toow")):
      return root[:-4]
    case "vti2":
      print(f"{verb!r} has an unrecognized {pos!r} final")
    case "vti3" if(root.endswith("nd")): # wund, piind, pumutaachiind
      return root[:-1]
    case "vti3" if(root.endswith("m")): # neem, kutaam, mulaam
      return root[:-1]
    case "vti3" if(root == "miichuw"): # miichii
      return root
    case "vti3":
      print(f"{verb!r} has an unrecognized {pos!r} final")

    # vaio
    case "vaio":
      print(f"{verb!r} has an unrecognized {pos!r} final")
    case "vtao":
      print(f"{verb!r} has an unrecognized {pos!r} final")

    # voti
    case "voti1a":
      print(f"{verb!r} has an unrecognized {pos!r} final")
    case "voti1b":
      print(f"{verb!r} has an unrecognized {pos!r} final")
    case "voti2":
      print(f"{verb!r} has an unrecognized {pos!r} final")

    # error
    case _:
      print(f"{pos!r} is not a valid verb type for {verb!r}")
  return 0

#endregion

#region Parser

#prenoun-root-nounsuffix
def nounParser(word, pos):
  functions_to_check = [
    check_prenoun,
    check_plural,
    check_locative,
    check_diminutive,
    check_nfin,
    check_reduplication
  ]

  word = remove_aliases(process_bracketed_string(word.replace('*', '')))

  for func in functions_to_check:
    result = func(word, pos)
    if result:
      return result

    # If none of the functions returned anything
  return None

def verbParser(word, pos):
  stem = findVerbStem(word, pos)
  #check for prefixes
  #check for suffixes
  #check for medials
  return word

def parser(word, pos):
  if pos.startswith('n'):
    return nounParser(word, pos)+'?'
  elif pos.startswith('v'):
    return verbParser(word, pos)+'?'
  return word+'?'

#endregion

def main():
  noun_test_cases = [
    ("na", "awehleeshoosh"),
    ("na", "amiimunzhush"),
    ("na", "ngukush"),
    ("ni", "naxkush"),
    ("na", "xuwiipambiil"),
    ("ni", "maxkasun"),
    ("ni", "maxkalaakwsiit"),
    ("ni", "miichuwaakan"),
    ("na", "pehpunawus"),
    ("na", "kiimooxkweew")]

  verb_test_cases = [
      ("vai", "muneew"),
      ("vai", "akiinsuw")
  ]

  test_cases = noun_test_cases + verb_test_cases

  for input_pos, input_str in test_cases:
    result = parser(input_str, input_pos)
    print(f"Input: {input_str}, Result: {result}")

    while True:
      input_str = input("Enter Word: ")
      if input_str.lower() == 'quit':
        break

      input_pos = input("Enter Part of Speech: ")
      if input_pos.lower() == 'quit':
        break

      result = parser(input_str, input_pos)
      print(f"Input: {input_str}, Result: {result}")