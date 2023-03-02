import openai
import subprocess
import json

# open reference code
with open("reference.py", "r") as f:
    ref_code = " ".join(f.readlines())

# prepare API call
openai.api_key = "PUT-YOUR-OWN-KEY"
messages = [
    {"role": "system", "content": "You are coding assistant. Provide only code."},
    {"role": "user", "content": "This is a reference code: " + ref_code},
]


while True:
    cmd = input("Provide a command: ")
    if cmd == "end":
        break
    msg = {
        "role": "user",
        "content": "Only using functions in the reference code "
        f"write a full code with all necessary imports for the following task: {cmd}"
        "If the task starts with remember ensure the code contains print."
        "Otherwise there is no need for explanation an do not output anything.```"
    }
    messages.append(msg)

    # call ChatGPT
    response = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=messages)
    chat_out = response["choices"][0]["message"]["content"]

    # save chat history
    msg = {"role": "assistant", "content": chat_out}
    messages.append(msg)

    if "fanucpy" in chat_out:
        # write to a python file
        with open("generated_code.py", "w") as f:
            code = chat_out.split("```")
            if len(code) > 1:
                code = code[1]
            else:
                code = code[0]
            code = code.strip("python")
            f.write(code)

        # run code in physical robot
        output = subprocess.check_output(["python", "generated_code.py"])
        print(output)
        msg = {"role": "assistant", "content": "generated output " + str(output)}
        messages.append(msg)

    with open("messages.json", "w") as f:
        json.dump(messages, f)
