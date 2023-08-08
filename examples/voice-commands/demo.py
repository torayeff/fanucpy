import json
import subprocess
import tkinter
import tkinter.messagebox
import wave

import openai
import pyaudio
from PIL import Image, ImageTk


class FanucVoiceCommand:
    def __init__(
        self,
        chunk=3024,
        frmat=pyaudio.paInt16,
        channels=1,
        rate=44100,
        py=pyaudio.PyAudio(),
    ):
        # prepare API call
        openai.api_key = "YOUR KEY"
        with open("initial-messages.json") as f:
            self.messages = json.load(f)

        # Start Tkinter and set Title
        self.main = tkinter.Tk()
        self.collections = []
        self.main.geometry("300x300")
        self.main.title("Record")
        self.CHUNK = chunk
        self.FORMAT = frmat
        self.CHANNELS = channels
        self.RATE = rate
        self.p = py
        self.frames = []
        self.st = 1
        self.stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )

        # Get the icons
        self.rec_icon = ImageTk.PhotoImage(
            Image.open("icons/rec.png").resize((300, 300))
        )
        self.stop_icon = ImageTk.PhotoImage(
            Image.open("icons/stop.png").resize((300, 300))
        )

        # Start and Stop buttons
        self.button = tkinter.Button(
            self.main,
            padx=10,
            pady=5,
            image=self.rec_icon,
            command=lambda: self.start_record(),
        )
        self.button.pack()
        tkinter.mainloop()

    def start_record(self):
        print("Provide a command: ")
        self.st = 1
        self.button.configure(command=lambda: self.stop(), image=self.stop_icon)
        self.frames = []
        stream = self.p.open(
            format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            frames_per_buffer=self.CHUNK,
        )
        while self.st == 1:
            data = stream.read(self.CHUNK)
            self.frames.append(data)
            print("* recording")
            self.main.update()

        stream.close()

        wf = wave.open("test_recording.wav", "wb")
        wf.setnchannels(self.CHANNELS)
        wf.setsampwidth(self.p.get_sample_size(self.FORMAT))
        wf.setframerate(self.RATE)
        wf.writeframes(b"".join(self.frames))
        wf.close()

        # Transcibe and execute the code
        transcription = self.whisper_transcribe()
        self.chat_gpt_exec(transcription)

    def whisper_transcribe(self):
        # Execute the rest.
        with open("test_recording.wav", "rb") as file:
            transcription = openai.Audio.transcribe("whisper-1", file)
        file.close()
        return transcription["text"]

    def chat_gpt_exec(self, cmd):
        msg = {
            "role": "user",
            "content": "Only using functions in the reference code "
            f"write a full code with all necessary imports for the following task: {cmd}"
            "If the task starts with remember ensure the code contains print."
            "Otherwise there is no need for explanation an do not output anything.```",
        }
        self.messages.append(msg)

        # call ChatGPT
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo", messages=self.messages
        )
        chat_out = response["choices"][0]["message"]["content"]
        print("Chat connection made.")

        # save chat history
        msg = {"role": "assistant", "content": chat_out}
        self.messages.append(msg)

        if "fanucpy" in chat_out:
            # write to a python file
            try:
                with open("generated_code.py", "w") as f:
                    code = chat_out.split("```")
                    if len(code) > 1:
                        code = code[1]
                    else:
                        code = code[0]
                    code = code.strip("python")
                    f.write(code)

                # run code in physical robot
                print("I am running the code.")
                output = subprocess.check_output(["python3.8", "generated_code.py"])
                print(output)
                msg = {
                    "role": "assistant",
                    "content": "generated output " + str(output),
                }
                self.messages.append(msg)
            except Exception as e:
                print(e)

        with open("messages.json", "w") as f:
            json.dump(self.messages, f)

    def stop(self):
        self.st = 0
        self.button.configure(command=lambda: self.start_record(), image=self.rec_icon)
        print("Stopped")


if __name__ == "__main__":
    fanucVoiceCommand = FanucVoiceCommand()
