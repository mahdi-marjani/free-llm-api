import re
import json
import asyncio
from playwright.async_api import async_playwright, Locator, Page
from playwright_stealth import Stealth


async def simulate_user_type(msg:str, msg_input:Locator, page:Page):
    msg_words = msg.strip().split('\n')

    for word_idx in range(len(msg_words)):
        if msg_words[word_idx] != '':
            await msg_input.type(msg_words[word_idx])
            if word_idx != len(msg_words) - 1:
                await page.keyboard.press('Shift+Enter')
        else:
            await page.keyboard.press('Shift+Enter')


def parse_gpt_response(stream_text: str) -> str:
    """
    Parse the stream response and extract the clean GPT message.
    Returns the concatenated text from the assistant's content.
    """
    # Step 1: Clean up prefixes and suffixes
    text_tmp1 = stream_text[33:] if stream_text.startswith("event: delta_encoding") else stream_text
    text_tmp1 = text_tmp1[7:] if text_tmp1.startswith("\ndata: ") else text_tmp1
    if text_tmp1.endswith("\n\ndata: [DONE]\n\n"):
        text_tmp2 = text_tmp1[:-16]
    else:
        text_tmp2 = text_tmp1
    
    # Step 2: Split into JSON chunks
    text_list = []
    for x in text_tmp2.replace("event: delta", "").split("\n\ndata: "):
        if x.strip():  # Skip empty
            tmp1 = x.strip()
            # Fix if not starting/ending with {} properly
            if not tmp1.startswith("{"):
                start_index = tmp1.find("{")
                if start_index != -1:
                    tmp1 = tmp1[start_index:]
            if not tmp1.endswith("}"):
                end_index = tmp1.rfind("}")
                if end_index != -1:
                    tmp1 = tmp1[:end_index + 1]
            # Try to load as JSON
            try:
                tmp = json.loads(tmp1)
            except json.JSONDecodeError:
                # Fix escaped backslashes if needed
                tmp2 = tmp1.replace("\\\\", "\\")
                try:
                    tmp = json.loads(tmp2)
                except json.JSONDecodeError:
                    continue  # Skip invalid chunks
            text_list.append(tmp)
    
    # Step 3: Find start of content and extract text
    first_begin = [i for i, msg in enumerate(text_list) if msg.get("p") == "/message/content/parts/0"]
    begin = first_begin[0] if first_begin else 0
    msg_list = ""
    for index, msg in enumerate(text_list):
        if index >= begin:
            # Simple string append
            if "v" in msg and isinstance(msg["v"], str):
                msg_list += msg["v"]
            # List handling (nested parts)
            elif "v" in msg and isinstance(msg["v"], list):
                for x in msg["v"]:
                    if "p" in x and x["p"] == "/message/content/parts/0" and "v" in x:
                        msg_list += x["v"]
                    # Deeper patch nesting
                    if "p" in x and x["p"] == "" and "o" in x and x["o"] == "patch" and "v" in x and isinstance(x["v"], list):
                        for sub in x["v"]:
                            if "p" in sub and sub["p"] == "/message/content/parts/0" and "v" in sub:
                                msg_list += sub["v"]
    
    # Step 4: Clean special patterns (if any, like in the original)
    if "turn0" in msg_list or "city" in msg_list:
        pattern = r'[\ue200-\ue203]?([a-z]+)?[\ue200-\ue203](?:turn\d+(?:image|search|fetch|forecast)\d+|city)'
        msg_list = re.sub(pattern, '', msg_list)
    
    return msg_list.strip()


async def send_msg(msg:str, page:Page):
    msg_input = page.locator('//textarea[@name="prompt-textarea"]')

    await simulate_user_type(msg, msg_input, page)
    
    async with page.expect_response("**/conversation") as response_info:
        await page.locator('//button[@aria-label="Send prompt"]').click()

    response = await response_info.value
    raw_stream = await response.text()
    answer = parse_gpt_response(raw_stream)

    return answer


async def main():
    async with Stealth().use_async(async_playwright()) as p:
        browser = await p.chromium.launch(headless = False)
        page = await browser.new_page()
        await page.goto("https://chatgpt.com/")

        answer = await send_msg('hi mate', page)
        print(f"GPT Response: {answer}")
        
        answer = await send_msg(
            'write factorial function with python and java and explain it and show me a sample table of input and outputs and explain more',
            page
        )
        print(f"GPT Response: {answer}")

asyncio.run(main())