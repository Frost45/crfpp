import CRFPP

class ExtendedTagger:

    def __init__(self): 
        self.transform_dict = {
            "B-NP": "nx",
            "B-VP": "vx",
            "B-ADJP": "adjp",
            "B-ADVP": "advp",
            "B-CONJP": "conjp",
            "B-INTJ": "intj",
            "B-LST": "lst",
            "B-PP": "pp",
            "B-PRT": "prt",
            "B-SBAR": "sbar",
            "B-UCP": "ucp",
        }

    def initialize_model(self, model_path):
        
        try:
            # -v 3: access deep information like alpha,beta,prob
            # -nN: enable nbest output. N should be >= 2
            self.tagger = CRFPP.Tagger(f"-m {model_path} -v 3 -n2")

        except:
            raise RuntimeError(f"{model_path} does not exist!")

    def get_chunks(self, word_list):

        output = []

        try:

            self.tagger.clear()
            
            for word in word_list:
                # Iterating over words and POSTags in sentence
                # and converting list to string and adding context to tagger
                # E.g. ["We", "PRP"] --> "We PRP"
                input_string = " ".join(word)
                self.tagger.add(input_string)

            # Parse added context and change tagger status to "parsed"
            self.tagger.parse()

            # Get total number of tokens from tagger
            # Each token has the word, POS_tag and chunk_tag
            size = self.tagger.size()

            for i in range(0, size):
                # tagger.y2(i) : Returns chunk_tag for i-th index
                # tagger.x(i, 0) : Returns word for i-th index
                # tagger.x(i, 1) : Returns POS_tag for i-th index as given by mxpost_tags
                chunk_list = [self.tagger.x(i, 0), self.tagger.x(i, 1), self.tagger.y2(i)]
                output.append(chunk_list)

        except:
            raise RuntimeError(f"Sentence could not be parsed!")

        return output


    def get_cass_chunks(self, word_list):

        try:
            chunker_output = self.get_chunks(word_list)
        except RuntimeError:
            raise

        tabs = '    '

        # Initializing output string for the chunked sentence
        output_string = "<s>\n"

        # This variable will be used to keep count of indentation level in output_string
        tabs_count = 1

        i = 0
        size = len(chunker_output)
        while i < size:

            chunk_list = chunker_output[i]

            if chunk_list[2] in self.transform_dict:
                # If chunk_tag refers to beginning of chunk, append transformed_chunk_tag
                # to output_string at current indentation level
                output_string += tabs * tabs_count + f"[{self.transform_dict[chunk_list[2]]}\n"

                # Increment indentation level and add all words and POS_tags 
                # in this chunk to output_string
                tabs_count += 1
                output_string += tabs * tabs_count + f"[{chunk_list[1].lower()} {chunk_list[0]}]"
                i += 1
                while i < size and chunk_list[2].startswith("I-"):
                    output_string += (
                        "\n"
                        + tabs * tabs_count
                        + f"[{chunk_list[1].lower()} {chunk_list[0]}]"
                    )
                    i += 1
                # Close current chunk and decrement indentation level
                output_string += "]\n"
                tabs_count -= 1
            else:
                # This else block takes care of the edge case of punctuation
                output_string += tabs * tabs_count + f"[per {chunk_list[0]}]\n"
                i += 1

        # Append chunked sentence to output and clear internal context
        return output_string

    def chunk_multiple_sentences(self, list_of_sentences, cass=False):

        output = []

        try:
            for sentence in list_of_sentences:
                if cass:
                    output.append(self.get_cass_chunks(sentence))
                else:
                    output.append(self.get_chunks(sentence))
        except RuntimeError:
            raise

        return output

