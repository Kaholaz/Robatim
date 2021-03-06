import collections
import logging
import random

from generate.idioms.score import Score

class Progression(Score):
	"""A framework for chord progressions"""

	PNode = collections.namedtuple("PNode", ["value", "stipulations"])

	def __init__(self):

		Progression.create_logger()

		# save memory
		empty_tuple = tuple()
		from_root_tonic = lambda: self.previous_chord == "0I"
		major_mode_only = lambda: self.mode == "ionian"
		minor_mode_only = lambda: self.mode == "aeolian"
		
		# can't store unhashable type (set) in hashable type tuple
		# tonic can come from other tonics and dominants
		# subdoms can come from other subdoms and tonics
		# dominants can come from tonics and subtonics

		not_plus_III = lambda: self.previous_chord != "+III"
		not_minus_III = lambda: self.previous_chord != "-III"
		not_secondary_dominants = (
			lambda: self.previous_chord[1:] not in self.secondary_dominants
		)
		NULL_I = self.PNode(
			"0I", (
				lambda: self.previous_chord not in ("+V42", "-IV6", "-VI", "-I6"),
				not_plus_III, not_minus_III, not_secondary_dominants
			)
		)
		NULL_VI6 = self.PNode("0VI6", (from_root_tonic,))
		prevent_ending = lambda: self.chord_index != 14
		NULL_I_MAJOR = self.PNode(
			"0I_MAJOR", (
				minor_mode_only, lambda: self.chord_index == 14, 
				lambda: not self.repeat_ending
			)
		)
		PLUS_I6 = self.PNode(
			"+I6", (
				lambda: self.previous_chord in (
					"+VII6", "+V43", "+V42", "0I", "+IV"
				),
				prevent_ending,
			)
		)
		MINUS_I6 = self.PNode(
			"-I6", (lambda: self.previous_chord in ("-IV6", "-VI"),)
		)

		from_positive_chord = lambda: self.previous_chord[0] in ("0", "+")
		from_negative_chord = lambda: self.previous_chord[0] == "-"
		validate_minus_V7 = (
			lambda: self.previous_chord in (
				"0I", "-I6", "+II", "-II", "-II7", "-II6", "-II65", "-IV", 
				"-IV_MAJOR", "-VI", "-IV6", "-IV6_MAJOR", "-IV7", "-V/V", 
				"+V/V", "-V6/V", "+V7/V","-V7/V","-V65/V", "-V43/V", "-VII6/V",
			)
		)
		validate_minus_V6 = (
			lambda: self.previous_chord in (
				"0I", "+I6", "+II", "+II6", "+IV", "-IV6", "-IV6_MAJOR", 
				"-IV65", "-IV65_MAJOR", "+II7", "+II65", "0II42", "0V42/V", 
				"-VII6/V", "-V43/V", "+III", "-VII_MAJOR"
			)
		)
		prevent_a2_with_V6 = (
			lambda: self.mode == "ionian" or self.previous_chord not in ("-IV6", "-IV65")
		)

		not_plus_II7 = lambda: self.previous_chord != "+II7"
		not_minus_II7 = lambda: self.previous_chord != "-II7"
		not_chord42 = lambda: "42" not in self.previous_chord
		PLUS_V = self.PNode("+V", (
				from_positive_chord, not_plus_II7, not_chord42, not_plus_III, 
			)
		)
		MINUS_V = self.PNode("-V", (validate_minus_V7, not_minus_II7)) 
		PLUS_V7 = self.PNode(
			"+V7", (from_positive_chord, not_chord42, not_secondary_dominants)
		)
		MINUS_V7 = self.PNode("-V7", (validate_minus_V7, not_secondary_dominants))
		MINUS_V6 = self.PNode("-V6", (validate_minus_V6, prevent_a2_with_V6))

		MINUS_V65 = self.PNode(
			"-V65", (validate_minus_V6, prevent_a2_with_V6)
		)
		PLUS_VII6 = self.PNode(
			"+VII6", (
				from_positive_chord, not_chord42, not_secondary_dominants,
			)
		)
		PLUS_V43 = self.PNode(
			"+V43", (
				from_positive_chord, not_chord42, not_secondary_dominants,
			)
		)
		PLUS_V42 = self.PNode(
			"+V42", (
				from_positive_chord, not_chord42, not_secondary_dominants,
			)
		)
		validate_minus_VIIMAJOR = lambda: self.previous_chord in ("0I", "-VI", "-IV6")
		MINUS_VIIMAJOR = self.PNode(
			"-VII_MAJOR", (
				validate_minus_VIIMAJOR, minor_mode_only,
			)
		)
		PLUS_VII6MAJOR = self.PNode(
			"+VII6_MAJOR", (
				lambda: self.previous_chord in ("0I" ,"+III"), minor_mode_only,
			)
		)

		MINUS_V_OF_III = self.PNode("-V/III", (from_root_tonic,))
		MINUS_V7_OF_III = self.PNode("-V7/III", (from_root_tonic,))
		PLUS_V6_OF_III = self.PNode("+V6/III", (from_root_tonic,))
		PLUS_V65_OF_III = self.PNode("+V65/III", (from_root_tonic,))
		PLUS_V43_OF_III = self.PNode("+V43/III", (from_root_tonic,))
		PLUS_VII6_OF_III = self.PNode("+VII6/III", (from_root_tonic,))

		PLUS_III = self.PNode(
			"+III", (
				lambda: self.previous_chord in (
					"-VII_MAJOR", "+VII6_MAJOR", "-V/III", "-V7/III", 
					"+V6/III", "+V65/III", "+V43/III", "+VII6/III"
				), prevent_ending
			)
		)
		MINUS_III = self.PNode(
			"-III", (lambda: self.previous_chord in ("-V/III", "-V7/III"),)
		)
		proper_subdom_order = (
			lambda: self.previous_chord not in (
				"+II", "-II", "+II6", "-II6", "+II65", "-II65", "+II7", "-II7", 
				"0II42", 
			)
		)

		no_major_mode_shift = lambda: self.previous_chord[-5:] != "MAJOR"
		no_minor_mode_shift = lambda: self.previous_chord[-5:] != "MINOR"

		not_plus_II6 = lambda: self.previous_chord != "+II6"
		not_minus_II6 = lambda: self.previous_chord != "-II6"
		not_plus_II = lambda: self.previous_chord != "+II"
		not_minus_II = lambda: self.previous_chord != "-II"

		maintain_seventh_tension = (
			lambda: self.previous_chord[-2:] not in ("65", "43", "42"),
			lambda: self.previous_chord[-1] != "7",
		)
		validate_plus_II = 	(
			lambda: self.mode == "ionian" or self.chord_index % 2 == 1 and 
				self.previous_chord in ("+II6", "+IV", "0VI6")
		)
		PLUS_II = self.PNode(
			"+II", (
				validate_plus_II, from_positive_chord, not_plus_III,
				*maintain_seventh_tension,
			)
		)
		#2Doms of V only appear as last subdom chord, 
		#so some potential rules are overlooked
		PLUS_V_OF_V = self.PNode(
			"+V/V", (
				validate_plus_II, from_positive_chord, not_plus_II,
				*maintain_seventh_tension, not_plus_III,
			)
		)
		PLUS_II6 = self.PNode(
			"+II6", (from_positive_chord, *maintain_seventh_tension)
		)
		PLUS_V6_OF_V = self.PNode(
			"+V6/V", (
				from_positive_chord, not_plus_II6, *maintain_seventh_tension,
				not_plus_III,
			)
		)
		not_sec_V = lambda: self.previous_chord[-2:] != "/V"
		PLUS_IV = self.PNode(
			"+IV", (
				proper_subdom_order, from_positive_chord, no_minor_mode_shift,
				*maintain_seventh_tension, not_sec_V
			)
		)
		PLUS_IVMAJOR = self.PNode(
			"+IV_MAJOR", (
				minor_mode_only, proper_subdom_order, from_positive_chord,
				*maintain_seventh_tension, lambda: self.previous_chord != "+IV",
				not_plus_III,
			)
		)
		MINUS_IVMAJOR = self.PNode(
			"-IV_MAJOR", (
				minor_mode_only, proper_subdom_order, from_negative_chord, 
				*maintain_seventh_tension, lambda: self.previous_chord != "-IV",
				not_minus_III,
			)
		)
		PLUS_IVMINOR = self.PNode(
			"+IV_MINOR", (
				major_mode_only, lambda: self.previous_chord == "+IV",
			)
		)

		lessen_deceptive_cadence = (
			lambda: self.chord_index != 8 or random.choice((True, True, True, False))
		)
		validate_minus_VI = lambda: self.previous_chord in ("0I", "-V", "0VI6")
		MINUS_VI = self.PNode(
			"-VI", (
				validate_minus_VI, prevent_ending, lessen_deceptive_cadence
			)
		)
		validate_minus_II = (				
			lambda: self.mode == "ionian" or self.chord_index % 2 == 1 and 
				self.previous_chord in ("-II6", "-IV")
		)
		MINUS_II = self.PNode(
			"-II", (
				validate_minus_II, from_negative_chord, *maintain_seventh_tension,
				not_minus_III
			)
		)
		MINUS_V_OF_V = self.PNode(
			"-V/V", (
				validate_minus_II, from_negative_chord, not_minus_II,
				*maintain_seventh_tension, not_minus_III
			)
		)
		MINUS_II6 = self.PNode(
			"-II6", (from_negative_chord, *maintain_seventh_tension)
		) 
		MINUS_V6_OF_V = self.PNode(
			"-V6/V", (
				from_negative_chord, not_minus_II6, *maintain_seventh_tension, 
				not_minus_III
			)
		)
		MINUS_IV = self.PNode(
			"-IV", (
				from_negative_chord, proper_subdom_order, *maintain_seventh_tension
			)
		)

		validate_minus_IV6 = (
			lambda: self.previous_chord in ("0I", "-VI", "-V", "-VII_MAJOR")
		)
		MINUS_IV6 = self.PNode("-IV6", (
			validate_minus_IV6, prevent_ending, lessen_deceptive_cadence
			)
		)
		MINUS_IV6MAJOR = self.PNode(
			"-IV6_MAJOR", (minor_mode_only, validate_minus_IV6)
		)
		MINUS_VII6_OF_V = self.PNode("-VII6/V", (validate_minus_IV6,))

		# II7 must go to V7 if it's the last subdom chord
		ante_section_only = lambda: self.chord_index < 8
		cons_section_only = lambda: self.chord_index >= 8
		PLUS_II65 = self.PNode(
			"+II65", (from_positive_chord, not_plus_II6, not_plus_III)
		)
		PLUS_V65_OF_V = self.PNode(
			"+V65/V", (
				from_positive_chord, not_plus_II6, *maintain_seventh_tension,
				not_plus_III
			)
		)
		MINUS_II65 = self.PNode(
			"-II65",(from_negative_chord, not_minus_II6, not_minus_III)
		)
		MINUS_V65_OF_V = self.PNode(
			"-V65/V", (
				from_negative_chord, not_minus_II6, *maintain_seventh_tension,
				not_minus_III,
			)
		)
		PLUS_II7 = self.PNode(
			"+II7", (from_positive_chord, not_plus_II, not_plus_III)
		)
		PLUS_V7_OF_V = self.PNode(
			"+V7/V", (
				from_positive_chord, not_plus_II, *maintain_seventh_tension,
				not_plus_III
			)
		)
		MINUS_II7 = self.PNode(
			"-II7", (
				from_negative_chord, not_minus_II, cons_section_only, 
				not_minus_III
			)
		)
		MINUS_V7_OF_V = self.PNode(
			"-V7/V", (
				from_negative_chord, not_minus_II, *maintain_seventh_tension,
				not_minus_III
			)
		)
		MINUS_V43_OF_V = self.PNode(
			"-V43/V", (
				from_negative_chord, not_minus_II, *maintain_seventh_tension, 
				not_minus_III
			)
		)
		NULL_II42 = self.PNode(
			"0II42", (from_positive_chord, ante_section_only, not_plus_III)
		)
		NULL_V42_OF_V = self.PNode(
			"0V42/V", (
				from_positive_chord, ante_section_only, not_plus_III,
				*maintain_seventh_tension,
			)
		)
		PLUS_IV7 = self.PNode(
			"+IV7", (
				from_positive_chord, proper_subdom_order, not_plus_III,
				lambda: self.previous_chord != "+IV", 	
			)
		)
		MINUS_IV7 = self.PNode(
			"-IV7", (
				from_negative_chord, proper_subdom_order, not_minus_III,
				lambda: self.previous_chord != "-IV",
			)
		)
		MINUS_IV65 = self.PNode(
			"-IV65", (major_mode_only, validate_minus_IV6, ante_section_only)
		)
		MINUS_IV65MAJOR = self.PNode(
			"-IV65_MAJOR", (minor_mode_only, validate_minus_IV6, ante_section_only)
		)
		not_secondary_V7 = lambda: self.previous_chord not in ("+V7/V", "+V65/V", "+V43/V", "0V42/V")
		PLUS_I64 = self.PNode(
			"+I64", (from_positive_chord, not_chord42, not_secondary_V7, not_plus_III)
		)

		# patterns ignore individual chord rules
		PATTERN_EXTEND5_DOUBLE01 = self.PNode(
			(MINUS_V, MINUS_V6, NULL_I), (validate_minus_V7, not_minus_II7)
		)
		PATTERN_EXTEND5_DOUBLE02 = self.PNode(
			(MINUS_V6, MINUS_V, NULL_I), (validate_minus_V6, prevent_a2_with_V6)
		)
		PATTERN_EXTEND5_DOUBLE03 = self.PNode(
			((MINUS_V6, MINUS_V65), (PLUS_V43, PLUS_VII6), NULL_I), 
			(from_root_tonic,)
		)
		PATTERN_EXTEND5_DOUBLE04 = self.PNode(
			(PLUS_V43, MINUS_V65, NULL_I), (from_root_tonic,)
		)
		PATTERN_EXTEND5_DOUBLE05 = self.PNode(
			(PLUS_V, PLUS_V42, PLUS_I6), (
				from_positive_chord, not_plus_II7, not_chord42, not_plus_III
			)
		)
		PATTERN_EXTEND5_DOUBLE06 = self.PNode(
			((PLUS_VII6, PLUS_V43), PLUS_V42, PLUS_I6), (from_root_tonic,)
		)
		PATTERN_EXTEND5_DOUBLE07 = self.PNode(
			((MINUS_V6, MINUS_V65), PLUS_V42, PLUS_I6), (from_root_tonic,)
		)
		PATTERN_EXTEND5_DOUBLE08 = self.PNode(
			(PLUS_V42, MINUS_V65, NULL_I), 
			(lambda: self.previous_chord == "+I6",)
		)
		PATTERN_EXTEND5_DOUBLE09 = self.PNode(
			(MINUS_VIIMAJOR, (MINUS_V6, MINUS_V65), NULL_I), 
			(from_root_tonic, minor_mode_only)
		)

		PATTERN_EXTEND5_DOUBLE10 = self.PNode(
			(PLUS_I64, PLUS_V, NULL_I), (
				from_positive_chord, not_chord42, not_secondary_V7, not_plus_III
			)
		)
		PATTERN_EXTEND5_DOUBLE11 = self.PNode(
			(PLUS_I64, MINUS_V, NULL_I), (
				from_positive_chord, not_chord42, not_secondary_V7, not_plus_III
			)
		)
		PATTERN_EXTEND5_DOUBLE12 = self.PNode(
			(PLUS_I64, PLUS_V42, PLUS_I6), (
				from_positive_chord, not_chord42, not_secondary_V7, not_plus_III
			)
		)
		PATTERN_EXTEND5_DOUBLE13 = self.PNode(
			(PLUS_I64, PLUS_V7, NULL_I), (
				from_positive_chord, not_chord42, not_secondary_V7, not_plus_III
			)
		)
		PATTERN_EXTEND5_DOUBLE14 = self.PNode(
			(PLUS_I64, MINUS_V7, NULL_I), (
				from_positive_chord, not_chord42, not_secondary_V7, not_plus_III
			)
		)
		PATTERN_EXTEND5_DOUBLE15 = self.PNode(
			(PLUS_IV, PLUS_IVMINOR, NULL_I), (
				major_mode_only, no_minor_mode_shift, proper_subdom_order, 
				from_positive_chord, *maintain_seventh_tension, 
				not_sec_V
			)
		)

		PATTERN_EXTEND5_DOUBLE20 = self.PNode(
			(PLUS_V43, NULL_I, MINUS_V6), (
				from_positive_chord, not_chord42, not_secondary_dominants
			)
		)
		PATTERN_EXTEND5_DOUBLE21 = self.PNode(
			(MINUS_V, MINUS_IV6, (MINUS_V6, MINUS_V65)), (
				major_mode_only, validate_minus_V7, not_minus_II7
			)
		)
		PATTERN_EXTEND5_DOUBLE22 = self.PNode(
			(MINUS_V, MINUS_VI, (MINUS_V6, MINUS_V65)), (
				major_mode_only, validate_minus_V7, not_minus_II7)
		)
		PATTERN_EXTEND5_DOUBLE23 = self.PNode(
			(MINUS_V, MINUS_IV6MAJOR, (MINUS_V6, MINUS_V65)), (
				minor_mode_only, validate_minus_V7, not_minus_II7
			)
		)
		PATTERN_EXTEND5_DOUBLE24 = self.PNode(
			(MINUS_V6, MINUS_IV6, MINUS_V), (
				major_mode_only, validate_minus_V6, prevent_a2_with_V6
			)
		)
		PATTERN_EXTEND5_DOUBLE25 = self.PNode(
			(MINUS_V6, MINUS_VI, MINUS_V), (
				major_mode_only, validate_minus_V6, prevent_a2_with_V6
			)
		)
		PATTERN_EXTEND5_DOUBLE26 = self.PNode(
			(MINUS_V6, MINUS_IV6MAJOR, MINUS_V), (
				minor_mode_only, validate_minus_V6, prevent_a2_with_V6
			)
		)
		PATTERN_EXTEND5_DOUBLE27 = self.PNode(
			(MINUS_VIIMAJOR, MINUS_IV6, MINUS_V),
			(minor_mode_only, validate_minus_VIIMAJOR)
		)
		PATTERN_EXTEND5_DOUBLE28 = self.PNode(
			((MINUS_V6, MINUS_V65), MINUS_IV6, MINUS_V7), (
				major_mode_only, validate_minus_V6, prevent_a2_with_V6
			) 
		)
		PATTERN_EXTEND5_DOUBLE29 = self.PNode(
			((MINUS_V6, MINUS_V65), MINUS_VI, MINUS_V7), (
				major_mode_only, validate_minus_V6, prevent_a2_with_V6
			)
		)
		PATTERN_EXTEND5_DOUBLE30 = self.PNode(
			((MINUS_V6, MINUS_V65), MINUS_IV6MAJOR, MINUS_V7), (
				minor_mode_only, validate_minus_V6, prevent_a2_with_V6
			)
		)
		PATTERN_EXTEND5_DOUBLE31 = self.PNode(
			(MINUS_VIIMAJOR, MINUS_IV6, MINUS_V7), 
			(minor_mode_only, validate_minus_VIIMAJOR)
		)


		not_minus_VI = lambda: self.previous_chord != "-VI"
		not_minus_IV6 = lambda: self.previous_chord != "-IV6"
		PATTERN_EXTEND2_DOUBLE01 = self.PNode(
			(PLUS_II, PLUS_I6, PLUS_II6), (				
				validate_plus_II, from_positive_chord, not_plus_III,
				*maintain_seventh_tension
			)
		)
		PATTERN_EXTEND2_DOUBLE02 = self.PNode(
			(PLUS_II6, PLUS_I6, PLUS_II), (
				from_positive_chord, *maintain_seventh_tension
			)
		)
		PATTERN_EXTEND2_DOUBLE03 = self.PNode(
			(NULL_I, MINUS_VI, (MINUS_IV, MINUS_II6)), (
				not_minus_VI, not_minus_IV6, not_plus_III, not_minus_III
			)
		)
		PATTERN_EXTEND2_DOUBLE04 = self.PNode(
			(NULL_I, MINUS_VI, MINUS_II), (
				major_mode_only, not_minus_VI, not_minus_IV6, not_plus_III, 
				not_minus_III
			)
		)
		PATTERN_EXTEND2_DOUBLE05 = self.PNode(
			(PLUS_II65, PLUS_I6, PLUS_II7), (
				from_positive_chord, not_plus_II6, not_plus_III
			)
		)
		PATTERN_EXTEND2_DOUBLE06 = self.PNode(
			(PLUS_II7, PLUS_I6, PLUS_II65), (
				from_positive_chord, not_plus_II, not_plus_III
			)
		)
		PATTERN_EXTEND2_DOUBLE07 = self.PNode(
			(MINUS_II, MINUS_I6, MINUS_II6), (
				validate_minus_II, from_negative_chord, not_minus_III,
				*maintain_seventh_tension, 
			)
		)
		PATTERN_EXTEND2_DOUBLE08 = self.PNode(
			(MINUS_II6, MINUS_I6, MINUS_II), (
				from_negative_chord, *maintain_seventh_tension
			)
		)
		PATTERN_EXTEND2_DOUBLE09 = self.PNode(
			(MINUS_II65, MINUS_I6, MINUS_II7), (
				from_negative_chord, not_minus_II6, cons_section_only, 
				not_minus_III
			)
		)
		PATTERN_EXTEND2_DOUBLE10 = self.PNode(
			(MINUS_II7, MINUS_I6, MINUS_II65), (
				from_negative_chord, not_minus_II, not_minus_III
			)
		)

		# don't forget to prevent abnormal endings
		self.tonic_chords_single = (
			NULL_I, PLUS_I6, NULL_I_MAJOR, (MINUS_VI, MINUS_IV6), MINUS_I6,
			PLUS_III, # MINUS_III, doesn't have progression for ante ending
		) 
		self.ante_ending_single = (
			PLUS_V, MINUS_V, (MINUS_V6, MINUS_V65), (PLUS_V43, PLUS_VII6), 
			PLUS_V42, (MINUS_VIIMAJOR, PLUS_VII6MAJOR),
		)
		self.tonic_extend_single = (
			(MINUS_V6, MINUS_V65), (PLUS_V43, PLUS_VII6), PLUS_V42, PLUS_IV, 
			(MINUS_IV6, MINUS_VI), MINUS_VIIMAJOR, PLUS_VII6MAJOR,
			(
				(MINUS_V_OF_III, MINUS_V7_OF_III), (PLUS_V6_OF_III, PLUS_V65_OF_III), 
				(PLUS_V43_OF_III, PLUS_VII6_OF_III)
			), 
		)
		# duplicates manipulate probability of chord
		self.cons_ending_single = (
			PLUS_V, MINUS_V, PLUS_V7, MINUS_V7, PLUS_IVMINOR, PLUS_IV, 
			MINUS_VIIMAJOR,
		)
		self.ante_ending_triple = (
			PATTERN_EXTEND5_DOUBLE01, PATTERN_EXTEND5_DOUBLE02,
			PATTERN_EXTEND5_DOUBLE03, PATTERN_EXTEND5_DOUBLE04,
			PATTERN_EXTEND5_DOUBLE05, PATTERN_EXTEND5_DOUBLE06,
			PATTERN_EXTEND5_DOUBLE07, PATTERN_EXTEND5_DOUBLE08,
			PATTERN_EXTEND2_DOUBLE09,
		)
		self.subdominant_single_minus1 = (
			PLUS_II, PLUS_II6, PLUS_IV, PLUS_IVMAJOR, MINUS_IVMAJOR, MINUS_VI, MINUS_II, 
			MINUS_II6, MINUS_IV, MINUS_VI, MINUS_IV6, MINUS_IV6MAJOR,
			PLUS_II7, PLUS_II65, MINUS_II7, MINUS_II65, NULL_II42,
			PLUS_IV7, MINUS_IV7, MINUS_IV65, MINUS_IV65MAJOR, 
		)
		self.alt_subdom_single_minus1 = (
			PLUS_V_OF_V, MINUS_V_OF_V, PLUS_V6_OF_V, MINUS_V6_OF_V, 
			PLUS_V7_OF_V, MINUS_V7_OF_V, PLUS_V65_OF_V, MINUS_V65_OF_V, 
			(MINUS_V43_OF_V, MINUS_VII6_OF_V), NULL_V42_OF_V
		)
		self.subdominant_single_minus2 = (
			PLUS_II, PLUS_II6, PLUS_IV, MINUS_VI, MINUS_II, MINUS_II6, MINUS_IV,
			MINUS_VI, MINUS_IV6, PLUS_II7, PLUS_II65, MINUS_II7, MINUS_II65, 
			NULL_VI6, NULL_VI6, NULL_VI6,
		)
		self.subdominant_triple = (
			PATTERN_EXTEND2_DOUBLE01, PATTERN_EXTEND2_DOUBLE02,
			PATTERN_EXTEND2_DOUBLE03, PATTERN_EXTEND2_DOUBLE04,
			PATTERN_EXTEND2_DOUBLE05, PATTERN_EXTEND2_DOUBLE06,
			PATTERN_EXTEND2_DOUBLE07, PATTERN_EXTEND2_DOUBLE08,
			PATTERN_EXTEND2_DOUBLE09, PATTERN_EXTEND2_DOUBLE10,
		)
		self.ante_plus1_64 = (
			PATTERN_EXTEND5_DOUBLE10, PATTERN_EXTEND5_DOUBLE11, 
			PATTERN_EXTEND5_DOUBLE12,
		)
		self.cons_plus1_64 = (
			PATTERN_EXTEND5_DOUBLE10, PATTERN_EXTEND5_DOUBLE11, 
			PATTERN_EXTEND5_DOUBLE13, PATTERN_EXTEND5_DOUBLE14,
		) 
		self.cons_ending_triple = (PATTERN_EXTEND5_DOUBLE15,)
		self.ante_dominant_extend_triple = (
			PATTERN_EXTEND5_DOUBLE20, PATTERN_EXTEND5_DOUBLE21, 
			PATTERN_EXTEND5_DOUBLE22, PATTERN_EXTEND5_DOUBLE23,
			PATTERN_EXTEND5_DOUBLE24, PATTERN_EXTEND5_DOUBLE25,
			PATTERN_EXTEND5_DOUBLE26, PATTERN_EXTEND5_DOUBLE27
		)
		self.cons_dominant_extend_triple = (
			PATTERN_EXTEND5_DOUBLE24, PATTERN_EXTEND5_DOUBLE25, 
			PATTERN_EXTEND5_DOUBLE26, PATTERN_EXTEND5_DOUBLE27, 
			PATTERN_EXTEND5_DOUBLE28, PATTERN_EXTEND5_DOUBLE29, 
			PATTERN_EXTEND5_DOUBLE30, PATTERN_EXTEND5_DOUBLE31
		)
		# starting chord is based on reverse membership testing of I and I6
		# previous chord is used on first index so it needs placeholder value
		self.previous_chord = "None"
		self.chord_index = 0

	def add_chord_pattern(self, chord_pattern):
		"""Generate new chord(s) for a chord progression"""

		empty_tuple = tuple()
		chord_pattern_functions = {
			"TON": self.add_one_chord, "RPT": self.repeat_chord,
			"1HC1": self.add_one_chord, "1HC2": self.add_one_chord,
			"1END_EX1": self.add_one_chord, "1EXTON1": self.add_one_chord,
			"1EXTON2": self.add_one_chord, "2HC": self.add_three_chords,
			"SDOM_AT_-1": self.add_one_chord, "SDOM_AF_-1": self.add_one_chord,
			"SDOM_AT_-2": self.add_one_chord, "3SDOM_EX": self.add_three_chords,
			"2END_EX1": self.add_three_chords, 
			"ANTE_3DOM_EX": self.add_three_chords,
			"CONS_3DOM_EX": self.add_three_chords,
		}
		chord_group_select = {
			"TON": (self.tonic_chords_single,), "RPT": empty_tuple,
			"1HC1": (self.ante_ending_single,),
			"1HC2": (self.tonic_chords_single,),
			"1END_EX1": (self.cons_ending_single,),
			"1EXTON1": (self.tonic_extend_single,),
			"1EXTON2": (self.tonic_chords_single,),
			"2HC": (
				empty_tuple, self.ante_ending_single, self.tonic_chords_single, 
				self.ante_ending_triple, self.ante_plus1_64
			), "SDOM_AT_-1": (
				self.subdominant_single_minus1, self.alt_subdom_single_minus1,
			), "SDOM_AF_-1": (
				self.subdominant_single_minus1, self.alt_subdom_single_minus1,
			), "SDOM_AT_-2": (self.subdominant_single_minus2,),
			"3SDOM_EX": (
				self.subdominant_single_minus1, self.tonic_chords_single, 
				self.subdominant_single_minus1, self.subdominant_triple,
			), "2END_EX1": (
				empty_tuple, self.cons_ending_single, self.tonic_chords_single,
				self.cons_ending_triple, self.cons_plus1_64
			), "ANTE_3DOM_EX": (
				self.ante_ending_single, self.tonic_chords_single,
				self.ante_ending_single, self.ante_dominant_extend_triple
			), "CONS_3DOM_EX": (
				self.cons_ending_single, self.tonic_chords_single,
				self.ante_ending_single, self.cons_dominant_extend_triple
			)
		}
		chord_adder = chord_pattern_functions[chord_pattern]
		self.logger.warning(f"Chord index: {self.chord_index}")
		self.logger.warning(f"Chord adder: {chord_adder.__name__}")
		chord_args = chord_group_select[chord_pattern]
		return chord_adder(*chord_args)

	def add_one_chord(self, *args):
		"""Generate the next chord in a progression based on score state"""

		all_valid_chords = []
		for chord_group in args:
			valid_chords = []
			for chord in chord_group:
				# account for interchangeable chords
				while not isinstance(chord, self.PNode):
					chord = random.choice(chord)
				self.logger.warning(f"Attempting: {chord.value}")
				# prevent repeat of subdom chords
				if (all(stipulation() for stipulation in chord.stipulations)
				  and chord.value != self.previous_chord):
					valid_chords.append(chord.value)
			if valid_chords:
				all_valid_chords.append(valid_chords)

		self.chord_index += 1
		self.logger.warning(f"All valid chords: {all_valid_chords}")
		chosen_chord_group = random.choice(all_valid_chords)
		self.previous_chord = random.choice(chosen_chord_group)
		self.logger.warning(f"Chosen chord: {self.previous_chord}")
		self.logger.warning("-" * 30)
		return self.previous_chord

	def add_three_chords(
	  self, chord_singlers, chord_doublers1, chord_doublers2, *args):
		"""Generate the next three chords in a progression based on chord state"""

		all_valid_chord_sequences = []
		temp_chord_index = self.chord_index
		temp_previous_chord = self.previous_chord
		for chord_group in args:
			valid_chord_sequences = []
			for chord_sequence in chord_group:
				self.logger.warning(chord_sequence)
				if all(stipulation() for stipulation in chord_sequence.stipulations):
					valid_chord_sequences.append(chord_sequence.value)

			if valid_chord_sequences:
				all_valid_chord_sequences.append(valid_chord_sequences)

		if not all_valid_chord_sequences:
			valid_chord_sequences = []

			# II6 II6 II doesn't work in minor mode
			# also weak-to-strong repetition
			for chord_double in chord_doublers1:
				self.previous_chord = temp_previous_chord
				self.chord_index = temp_chord_index
				while not isinstance(chord_double, self.PNode):
					chord_double = random.choice(chord_double)
				self.logger.warning(chord_double)
				if all(stipulation() for stipulation in chord_double.stipulations):
					self.previous_chord = chord_double.value
					self.chord_index += 2
					for chord_single in chord_doublers2:
						while not isinstance(chord_single, self.PNode):
							chord_single = random.choice(chord_single)
						self.logger.warning(chord_single)
						if all(stipulation() for stipulation in chord_single.stipulations):
							valid_chord_sequences.append(
								(chord_double, chord_double, chord_single)
							)
			self.previous_chord = temp_previous_chord
			self.chord_index = temp_chord_index
			all_valid_chord_sequences.append(valid_chord_sequences)

			if chord_singlers:
				valid_chord_sequences = []
				for chord_single in chord_singlers:
					while not isinstance(chord_single, self.PNode):
						chord_single = random.choice(chord_single)
					self.logger.warning(chord_single)
					if all(stipulation() for stipulation in chord_single.stipulations):
						valid_chord_sequences.append(
							(chord_single, chord_single, chord_single)
						)
				all_valid_chord_sequences.append(valid_chord_sequences)

		self.logger.warning(f"Valid chord groups: {all_valid_chord_sequences}")
		chosen_chord_group = random.choice(all_valid_chord_sequences)
		chosen_chord_items = random.choice(chosen_chord_group)
		chosen_chord_sequence = []
		for chord_item in chosen_chord_items:
			if isinstance(chord_item, self.PNode):
				chosen_chord_sequence.append(chord_item.value)
			elif isinstance(chord_item, tuple):
				chosen_chord_sequence.append(random.choice(chord_item).value)

		self.chord_index += len(chosen_chord_sequence)
		self.previous_chord = chosen_chord_sequence[-1]
		self.logger.warning(f"Chosen chord sequences: {chosen_chord_sequence}")
		self.logger.warning("-" * 30)
		return chosen_chord_sequence

	def repeat_chord(self):	
		self.chord_index += 1
		return self.previous_chord

	@staticmethod
	def choose_progression_type():
		"""Choose a pattern for a full chord progression"""

		antecedent_patterns = (
			("TON", "RPT", "RPT", "RPT", "RPT", "RPT", "1HC1", "RPT", "1HC2"),
			("TON", "RPT", "RPT", "RPT", "RPT", "RPT", "2HC"),
			("TON", "RPT", "RPT", "1EXTON1", "1EXTON2", "RPT", "1HC1", "RPT", "1HC2"),
			("TON", "RPT", "RPT", "1EXTON1", "1EXTON2", "RPT", "2HC"),
			("TON", "RPT", "1EXTON1", "RPT", "1EXTON2", "RPT", "1HC1", "RPT", "1HC2"),
			("TON", "RPT", "1EXTON1", "RPT", "1EXTON2", "RPT", "2HC"),

			("TON", "RPT", "RPT", "RPT", "SDOM_AT_-1", "RPT", "1HC1", "RPT", "1HC2"),
			("TON", "RPT", "RPT", "RPT", "SDOM_AT_-1", "RPT", "2HC"),
			("TON", "RPT", "RPT", "RPT", "RPT", "SDOM_AF_-1", "1HC1", "RPT", "1HC2"),
			("TON", "RPT", "RPT", "RPT", "RPT", "SDOM_AF_-1", "2HC"),
			
			("TON", "RPT", "RPT", "1EXTON1", "1EXTON2", "SDOM_AF_-1", "1HC1", "RPT", "1HC2"),
			("TON", "RPT", "RPT", "1EXTON1", "1EXTON2", "SDOM_AF_-1", "2HC"),
			("TON", "RPT", "1EXTON1", "RPT", "1EXTON2", "SDOM_AF_-1", "1HC1", "RPT", "1HC2"),
			("TON", "RPT", "1EXTON1", "RPT", "1EXTON2", "SDOM_AF_-1", "2HC"),
			("TON", "RPT", "RPT", "RPT", "SDOM_AT_-2", "SDOM_AF_-1", "1HC1", "RPT", "1HC2"),

			("TON", "RPT", "RPT", "RPT", "ANTE_3DOM_EX", "RPT", "1HC2"),
		)
		consequent_patterns = (
			("RPT", "RPT", "RPT", "RPT", "1END_EX1", "TON", "RPT"),
			("RPT", "RPT", "RPT", "1END_EX1", "RPT", "TON", "RPT"),

			("RPT", "RPT", "RPT", "SDOM_AT_-1", "1END_EX1", "TON", "RPT"),
			("RPT", "SDOM_AT_-1", "RPT", "1END_EX1", "RPT", "TON", "RPT"),
			("RPT", "RPT", "SDOM_AF_-1", "1END_EX1", "RPT", "TON", "RPT"),
			("RPT", "3SDOM_EX", "1END_EX1", "TON", "RPT"),
			("RPT", "RPT", "RPT", "2END_EX1", "RPT"),
			("RPT", "SDOM_AT_-1", "RPT", "2END_EX1", "RPT"),
			("RPT", "RPT", "SDOM_AF_-1", "2END_EX1", "RPT"),
			("RPT", "SDOM_AT_-2", "SDOM_AF_-1", "2END_EX1", "RPT"),

			("RPT", "CONS_3DOM_EX", "RPT","TON", "RPT"),
		)

		all_progression_types = {}
		for antecedent_pattern in antecedent_patterns:
			for consequent_pattern in consequent_patterns:
				full_pattern = antecedent_pattern + consequent_pattern
				if (len(full_pattern) == 16 and 
				  Progression.allows_truncation(full_pattern, 2, "RPT")):
					accelerate = False
				else:
					accelerate = True
				all_progression_types[full_pattern] = accelerate

		progression_type = random.choice(tuple(all_progression_types))
		return progression_type, all_progression_types[progression_type]

	@staticmethod
	def allows_truncation(sequence, divisor, repeat_value):
		"""Check last item equality of list dividends"""
		
		if divisor < 2:
			return False
		if len(sequence) < divisor:
			return False

		for item_num, current_item in enumerate(sequence, 1):
			if item_num % divisor == 0 and current_item != repeat_value:
				return False
		return True
