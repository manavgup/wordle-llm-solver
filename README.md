# LLM-Powered Wordle-Solver 

This is a Wordle-solving script powered by LLM (Large Language Model) and built using IBM watsonx and SeleniumBase.

![Wordle solver winning!](images/wordle_llm.gif "Wordle-Solver winning!")

## Prerequisites

In order to run this program, you will need the following:

- Python 3.7 or higher
- SeleniumBase installed
- enchant library installed 
- watsonx API key

This script works by utilizing the power of LLMs to play Wordle like a Human. The program takes a screenshot of the Wordle game, observes the result colors, and then generates a guess word based on the history and the letters available in the puzzle. 

The program then uses SeleniumBase, an "All-in-one Test Automation Framework" for automation of browser interactions, to input the potential solutions into the Wordle game and check their correctness. It repeats this process until the guess word have been successfully guessed or the number of guesses is reached.

## How to run

```pip install -r requirements.txt```

Add your watsonx key and other credentials in ```.env``` 

### for watsonx
```
URL=
APIKEY=
PROJECT_ID=
```

### for OpenAI
```
OPENAI_API_KEY=
OPENAI_ORG_ID=
```


Open a terminal or command prompt and navigate to the directory where the program is located.

Run the program by typing the following command:
```
python wordleTest.py
```

Sit back and relax as the program solves the puzzle for you!

## Conclusion

While LLMs have vast knowledge of words themselves, they currently lack many of the reasoning skills, strategies, and broader understanding of linguistic dynamics and games that allow humans to efficiently narrow down options and deduce solutions. Researchers are actively working on developing more capable reasoning and inference abilities for LLMs..  