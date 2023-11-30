from ibm_watson_machine_learning.foundation_models.utils.enums import ModelTypes
from ibm_watson_machine_learning.foundation_models import Model
from ibm_watson_machine_learning.metanames import GenTextParamsMetaNames as GenParams
from ibm_watson_machine_learning.foundation_models.utils.enums import DecodingMethods
import re
import random
import enchant

class LlmWordleSolver:

    def __init__(self, my_credentials, project_id):
        
        # parameters for watsonx llm
        self.parameters = {
            GenParams.DECODING_METHOD: DecodingMethods.SAMPLE,
            GenParams.MIN_NEW_TOKENS: 1,
            GenParams.MAX_NEW_TOKENS: 5,
            GenParams.RANDOM_SEED: 1337,
            GenParams.TEMPERATURE: 0.6,
            GenParams.TOP_K: 50,
            GenParams.TOP_P: 1,
            GenParams.REPETITION_PENALTY: 1.18
        }
        self.space_id    = None # required by watonx library
        self.verify      = False # required by watsonx library
        self.credentials = my_credentials
        self.projectid = project_id
        self.dictionary = enchant.Dict("en-US")

        self.history = []
        self.invalidLetters = []
        self.letterPositions = {}
        self.currentStatus = ["X","X","X","X","X"]
        self.includeLetters = []
        self.promptText = ""
        self.prompt = ""

        # self.context["valid_letter_word"] = "-----"

        self.model = Model(ModelTypes.LLAMA_2_70B_CHAT, 
                            my_credentials, 
                                self.parameters, 
                                    project_id, 
                                        self.space_id, 
                                            self.verify)
    

    ###########################################Utility Functions###############################################
    def get_prompt(self):
        return f"""### Instruction: 
        Play the wordle game by providing a 5 letter English language word. 
        Correct guess for each letter is denoted by G (correct letter in correct position), X (invalid letter), or Y (correct letter in wrong position). Current status is shown after the text "Current Status:".
        For example:
        APPLE
        XXXGX
        Here L is a valid letter in the final word and in the correct position.
        Follow the instructions below:
        Respond only with a 5 letter word as your answer. Do not respond with anything else.
        Do not use any letters from the invalid letters provided to you.
        Do not use any invalid letters in your response.
        Do not repeat any letters from history. 
        Always include letters from the "Include Letters" list in your response.
        Once a letter is in the correct position, your guess should always have that letter in the same position.
        Respond with only a 5 letter word.
        Your response should be a valid English word.
        Do not reply with reasoning and explanation. Only reply with the guess word.
        Do not start your response with 'Sure! my guess is'.
        Do not start your response with "sure" or "my" or "here".
        {self.promptText}
        History: {self.history}
        Invalid letters: {self.invalidLetters}
        Include Letters: {self.includeLetters}
        Current Status: {self.currentStatus}
        Guess the correct 5 letter word.
        ### Response: """
    
    # Getter for invalidLetters
    def get_invalid_letters(self):
        return self.invalidLetters
    
      # Setter for invalidLetters
    def update_invalid_letters(self, new_letter: str):
        self.invalidLetters.append(str)

   # Getter for history
    def get_history(self):
        return self.history
    
      # Setter for history
    def update_history(self, word: str):
        self.history = ','.join([self.history, word]) if self.history else word

    def extract_entity(self, llm_response: str):
        #parameters for watsonx llm
        entity_parameters = {
            GenParams.DECODING_METHOD: DecodingMethods.SAMPLE,
            GenParams.MIN_NEW_TOKENS: 2,
            GenParams.MAX_NEW_TOKENS: 2,
            GenParams.RANDOM_SEED: 1024,
            GenParams.TEMPERATURE: 0.7,
            GenParams.TOP_K: 50,
            GenParams.TOP_P: 1,
            GenParams.REPETITION_PENALTY: 1
        }
        
        entity_model = Model(ModelTypes.LLAMA_2_70B_CHAT, 
                            credentials=self.credentials, 
                            params=entity_parameters, 
                            project_id=self.projectid, 
                            space_id=self.space_id, 
                            verify=self.verify)
            
        entity_prompt = f"""Extract the 5 letter guess word from the text below:
        {llm_response}
        """
        print (f"Entity Prompt: {entity_prompt}")
        entity = entity_model.generate_text(entity_prompt)
        print (f"--> entity returned by watsonx: {entity}")
        return entity.strip()

    def guessWord(self):

        generated_text = ""
        while True:
            prompt = self.get_prompt()
            self.parameters['temperature'] = random.uniform(0.6, 1)
            print(f"Prompt: {prompt}")
            generated_text = self.model.generate_text(prompt).strip().lower()
            print(f"watsonx result: {generated_text}")
            # extract_text = self.extract_entity(generated_text)
            if len(generated_text) == 5 and bool(re.match('^[a-zA-Z0-9]*$', generated_text)) == True and self.dictionary.check(generated_text) and generated_text not in self.history:
                break
            else:
                self.update_history(generated_text)

        return generated_text.strip()


    def update_current_status(self, word, letter_status):
        for i in range(len(word)):
            #self.updateWordPositions(word[i], letter_status[i], i+1, word)
            if letter_status[i] == "correct":
                self.currentStatus[i] = 'G'
                if word[i] not in self.includeLetters:
                    self.includeLetters.append(word[i])
            elif letter_status[i] == "present":
                self.currentStatus[i] = 'Y'
                if word[i] not in self.includeLetters:
                    self.includeLetters.append(word[i])                
            elif letter_status[i] == 'absent':
                self.currentStatus[i] = 'X'
                if word[i] not in self.invalidLetters:
                    self.invalidLetters.append(word[i])
       
    def updateWordPositions(self, letter: str, status: str, position: int, word: str):
        if status == "correct":
            self.promptText += f"The letter at position {position} must be {letter}. "
        elif status == "present":
            self.promptText += f"The word must include {letter}. Do not respond with {word}. "

    def updateValidLettersWord(self, last_guess: str, guess_result: str):
        for i in range(len(last_guess)):
            if guess_result[i] == 'G':
                if self.context["valid_letter_word"][i] != last_guess[i]:
                    self.context["valid_letter_word"] = self.context["valid_letter_word"][:i] + last_guess[i] + self.context["valid_letter_word"][i:]

    def sort_letters(self, last_guess: str, guess_result: str):
        for i in range(len(last_guess)):
            if guess_result[i] == 'G' or guess_result[i] == 'Y':
                if last_guess[i] not in self.context["valid_letters"]:
                    self.context["valid_letters"] += f"{last_guess[i]} "
            else:
                if last_guess[i] not in self.context["invalid_letters"]:
                    self.context["invalid_letters"] += f"{last_guess[i]} "