from pyrogram import Client, filters
import requests, os, asyncio, threading
from config import TELEGRAM_BOT_TOKEN, API_ID, API_HASH, DATABASE_URI

app = Client("classplus_bot", api_id=API_ID, api_hash=API_HASH, bot_token=TELEGRAM_BOT_TOKEN)

api = 'https://api.classplusapp.com/v2'

headers = {
    "Host": "api.classplusapp.com",
    "x-access-token": "",
    "User-Agent": "Mobile-Android",
    "Accept": "application/json, text/plain, */*",
    "Origin": "https://web.classplusapp.com",
    "Referer": "https://web.classplusapp.com/",
    "Region": "IN",
}

# ---- CareerWill Handler ----
import threading

ACCOUNT_ID = "6206459123001"
BCOV_POLICY = "BCpkADawqM1474MvKwYlMRZNBPoqkJY-UWm7zE1U769d5r5kqTjG0v8L-THXuVZtdIQJpfMPB37L_VJQxTKeNeLO2Eac_yMywEgyV9GjFDQ2LTiT4FEiHhKAUvdbx9ku6fGnQKSMB8J5uIDd"
bc_url = f"https://edge.api.brightcove.com/playback/v1/accounts/{ACCOUNT_ID}/videos/"
bc_hdr = {"BCOV-POLICY": BCOV_POLICY}

async def careerdl(app, message, headers, raw_text2, raw_text3, prog, name):
    num_id = raw_text3.split('&')
    for x in range(0, len(num_id)):
        id_text = num_id[x]
        details_url = "https://elearn.crwilladmin.com/api/v3/batch-detail/" + raw_text2 + "?topicId=" + id_text
        response = requests.get(details_url, headers=headers)
        data = response.json()
        details_list = data["data"]["class_list"]
        batch_class = details_list["classes"]
        batch_class.reverse()
        fuck = ""
        try:
            for data in batch_class:
                vid_id = data['id']
                lesson_name = data['lessonName']
                lessonExt = data['lessonExt']
                url = "https://elearn.crwilladmin.com/api/v3/class-detail/" + vid_id
                lessonUrl = requests.get(url, headers=headers).json()['data']['class_detail']['lessonUrl']
                if lessonExt == 'brightcove':
                    url = "https://elearn.crwilladmin.com/api/v3/livestreamToken"
                    params = {
                        "base": "web",
                        "module": "batch",
                        "type": "brightcove",
                        "vid": vid_id
                    }
                    response = requests.get(url, headers=headers, params=params)
                    stoken = response.json()["data"]["token"]
                    link = bc_url + lessonUrl + "/master.m3u8?bcov_auth=" + stoken
                    fuck += f"{lesson_name}: {link}\n"
                elif lessonExt == 'youtube':
                    link = "https://www.youtube.com/embed/" + lessonUrl
                    fuck += f"{lesson_name}: {link}\n"
            if '/' in name:
                name1 = name.replace("/", "")
            else:
                name1 = name
            with open(f"{name1}.txt", 'a') as f:
                f.write(f"{fuck}")
        except Exception as e:
            await message.reply_text(str(e))
    c_txt = f"**App Name: CareerWill\nBatch Name: `{name}`**"
    await app.send_document(message.chat.id, document=f"{name1}.txt", caption=c_txt)
    await prog.delete()
    os.remove(f"{name1}.txt")

@app.on_message(filters.command("careerwill"))
async def career_will(client, message):
    try:
        input1 = await client.ask(message.chat.id, text="**Send ID & Password in this manner otherwise bot will not respond.\n\nSend like this:-  ID*Password\n\n OR Send Your Token**")
        login_url = "https://elearn.crwilladmin.com/api/v3/login-other"
        raw_text = input1.text
        if "*" in raw_text:
            headers = {
                "Host": "elearn.crwilladmin.com",
                "origintype": "web",
                "accept": "application/json",
                "content-type": "application/json; charset=utf-8",
                "accept-encoding": "gzip",
                "user-agent": "okhttp/3.9.1"
            }
            email, password = raw_text.split("*")
            data = {
                "deviceType": "web",
                "password": password,
                "deviceModel": "chrome",
                "deviceVersion": "Chrome+119",
                "email": email
            }
            response = requests.post(login_url, headers=headers, json=data)
            response.raise_for_status()  # Raise an error if the request was unsuccessful
            token = response.json()["data"]["token"]
            await message.reply_text(f"**Login Successful**\n\n`{token}`")
        else:
            token = raw_text
    except Exception as e:
        await message.reply_text(f"An error occurred during login: {e}")
        return
    headers = {
        "Host": "elearn.crwilladmin.com",
        "origintype": "web",
        "usertype": "2",
        "token": token,
        "accept-encoding": "gzip",
        "user-agent": "okhttp/3.9.1"
    }
    await input1.delete(True)
    batch_url = "https://elearn.crwilladmin.com/api/v3/my-batch"
    response = requests.get(batch_url, headers=headers)
    data = response.json()
    topicid = data["data"]["batchData"]
    FFF = "**BATCH-ID     -     BATCH NAME**\n\n"
    for data in topicid:
        FFF += f"`{data['id']}`     -    **{data['batchName']}**\n\n"
    await message.reply_text(f"**HERE IS YOUR BATCH**\n\n{FFF}")
    input2 = await client.ask(message.chat.id, text="**Now send the Batch ID to Download**")
    raw_text2 = input2.text
    topic_url = "https://elearn.crwilladmin.com/api/v3/batch-topic/" + raw_text2 + "?type=class"
    response = requests.get(topic_url, headers=headers)
    topic_data = response.json()
    batch_data = topic_data['data']['batch_topic']
    name = topic_data["data"]["batch_detail"]["name"]
    BBB = "**TOPIC-ID - TOPIC**\n\n"
    id_num = ""
    for data in batch_data:
        topic_id = data["id"]
        topic_name = data["topicName"]
        id_num += f"{topic_id}&"
        BBB += f"`{topic_id}` -  **{topic_name}** \n\n"
    await message.reply_text(f"**Batches details of {name}**\n\n{BBB}")
    input3 = await client.ask(message.chat.id, text=f"Now send the **Topic IDs** to Download\n\nSend like this **1&2&3&4** so on\nor copy paste or edit **below ids** according to you :\n\n**Enter this to download full batch :-**\n`{id_num}`")
    raw_text3 = input3.text
    prog = await message.reply_text("**Extracting Videos Links Please Wait  📥 **")
    try:
        thread = threading.Thread(target=lambda: asyncio.run(careerdl(client, message, headers, raw_text2, raw_text3, prog, name)))
        thread.start()
    except Exception as e:
        await message.reply_text(str(e))


def get_course_content(course_id, folder_id=0):
    fetched_contents = ""
    params = {'courseId': course_id, 'folderId': folder_id}
    res = requests.get(f'{api}/course/content/get', headers=headers, params=params)
    if res.status_code == 200:
        res_json = res.json()
        contents = res_json.get('data', {}).get('courseContent', [])
        for content in contents:
            if content['contentType'] == 1:
                sub_contents = get_course_content(course_id, content['id'])
                fetched_contents += sub_contents
            elif content['contentType'] == 2:
                name = content.get('name', '')
                url = requests.get(f'{api}/cams/uploader/video/jw-signed-url', headers=headers, params={'contentId': content['contentHashId']}).json()['url']
                fetched_contents += f'{name}:{url}\n'
            else:
                fetched_contents += f"{content.get('name', '')}:{content.get('url', '')}\n"
    return fetched_contents


@app.on_message(filters.command("login"))
async def classplus_login(client, message):
    try:
        input_msg = await message.reply_text("Send your credentials as shown below:\n\nORG CODE:\nMOBILE NUMBER:\n\nOR\n\nACCESS TOKEN:")
        input_response = await client.listen(message.chat.id)
        creds = input_response.text.strip()

        if '\n' in creds:
            org_code, phone_no = [cred.strip() for cred in creds.split('\n')]
            res = requests.get(f'{api}/orgs/{org_code}')
            if res.status_code == 200:
                org_id = res.json()['data']['orgId']
                data = {'countryExt': '91', 'mobile': phone_no, 'orgCode': org_code, 'orgId': org_id, 'viaSms': 1}
                res = requests.post(f'{api}/otp/generate', data=data, headers=headers)
                if res.status_code == 200:
                    otp_msg = await message.reply_text("Send your OTP:")
                    otp_response = await client.listen(message.chat.id)
                    otp = otp_response.text.strip()
                    data = {"otp": otp, "countryExt": "91", "sessionId": res.json()['data']['sessionId'], "orgId": org_id, "mobile": phone_no}
                    res = requests.post(f'{api}/users/verify', data=data, headers=headers)
                    if res.status_code == 200:
                        token = res.json()['data']['token']
                        headers['x-access-token'] = token
                        await message.reply_text(f"Login Successful! Token:\n`{token}`\n\nSend /courses to continue.")
                    else:
                        await message.reply_text("OTP Verification Failed.")
                else:
                    await message.reply_text("Failed to generate OTP.")
            else:
                await message.reply_text("Invalid ORG Code.")
        else:
            token = creds.strip()
            headers['x-access-token'] = token
            res = requests.get(f'{api}/users/details', headers=headers)
            if res.status_code == 200:
                await message.reply_text("Login Successful! Send /courses to continue.")
            else:
                await message.reply_text("Invalid Token. Try Again.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")


@app.on_message(filters.command("courses"))
async def classplus_courses(client, message):
    try:
        user_id = headers.get('x-access-token')
        res = requests.get(f'{api}/profiles/users/data', headers=headers, params={'userId': user_id, 'tabCategoryId': 3})
        if res.status_code == 200:
            res_json = res.json()
            courses = res_json['data']['responseData']['coursesData']
            if courses:
                text = '\n'.join([f"{i+1}. {course['name']}" for i, course in enumerate(courses)])
                num = await message.reply_text(f"Send the index number of the course to download:\n\n{text}")
                num_response = await client.listen(message.chat.id)
                selected_course_index = int(num_response.text.strip()) - 1
                course_id = courses[selected_course_index]['id']
                course_name = courses[selected_course_index]['name']
                msg = await message.reply_text("Extracting course content...")
                course_content = get_course_content(course_id)
                await msg.delete()
                if course_content:
                    with open("Classplus.txt", 'w') as f:
                        f.write(course_content)
                    await message.reply_document("Classplus.txt", caption=f"Batch Name: {course_name}")
                    os.remove("Classplus.txt")
                else:
                    await message.reply_text("No content found in the course.")
            else:
                await message.reply_text("No courses found.")
        else:
            await message.reply_text("Failed to fetch courses.")
    except Exception as e:
        await message.reply_text(f"Error: {e}")

# ---- RG Vikramjeet Handler ----
import json
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

def decrypt_data(encoded_data):
    key = "638udh3829162018".encode("utf8")
    iv = "fedcba9876543210".encode("utf8")
    decoded_data = b64decode(encoded_data)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted_data = unpad(cipher.decrypt(decoded_data), AES.block_size)
    return decrypted_data.decode('utf-8')

async def rgvikram_down(app, message, hdr1, api, raw_text2, fuk, batch_name, name, prog):
    vt = ""
    try:
        xx = fuk.split('&')
        for f in xx:
            res3 = requests.get(f"https://{api}/get/alltopicfrmlivecourseclass?courseid=" + raw_text2 + "&subjectid=" + f + "&start=-1", headers=hdr1)
            b_data2 = res3.json().get('data', [])
            vp = ""
            for data in b_data2:
                tid = data.get("topicid")
                if tid:
                    vp += f"{tid}&"
            vj = ""
            try:
                xv = vp.split('&')
                for y in range(len(xv)):
                    t = xv[y]
                    res4 = requests.get(f"https://{api}/get/livecourseclassbycoursesubtopconceptapiv3?courseid=" + raw_text2 + "&subjectid=" + f + "&topicid=" + t + "&conceptid=1&start=-1", headers=hdr1).json()
                    topicid1 = res4.get("data", [])
                    for data in topicid1:
                        type = data.get('material_type')
                        tid = data.get("Title")
                        if type == 'VIDEO':
                            if data.get('ytFlag') == 0:
                                dlink = next((link['path'] for link in data.get('download_links', []) if link.get('quality') == "720p"), None)
                                if dlink:
                                    parts = dlink.split(':')
                                    if len(parts) == 2:   
                                        encoded_part, encrypted_part = parts
                                        b = decrypt_data(encoded_part)
                                        cool2 = f"{b}"
                                    else:
                                        print(f"Unexpected format: {plink}\n{tid}")
                            elif data.get('ytFlag') == 1:
                                dlink = data.get('file_link')
                                if dlink:
                                    encoded_part, encrypted_part = dlink.split(':')
                                    b = decrypt_data(encoded_part)
                                    cool2 = f"{b}"
                                else:
                                    print(f"Missing video_id for {tid}")
                            else:
                                print("Unknown ytFlag value")
                            msg = f"{tid} : {cool2}\n"
                            vj += msg
                        elif type == 'PDF':
                            plink = data.get("pdf_link", "").split(':')
                            if len(plink) == 2:
                                encoded_part, encrypted_part = plink
                                vs = decrypt_data(encoded_part)
                                msg = f"{tid} : {vs}\n"
                                vj += msg
                    res5 = requests.get(f"https://{api}/get/livecourseclassbycoursesubtopconceptapiv3?courseid=" + raw_text2 + "&subjectid=" + f + "&topicid=" + t + "&conceptid=2&start=-1", headers=hdr1).json()
                    topicid2 = res5.get("data", [])
                    for data in topicid2:
                        type = data.get('material_type')
                        tid = data.get("Title")
                        if type == 'VIDEO':
                            if data.get('ytFlag') == 0:
                                dlink = next((link['path'] for link in data.get('download_links', []) if link.get('quality') == "720p"), None)
                                if dlink:
                                    parts = dlink.split(':')
                                    if len(parts) == 2:   
                                        encoded_part, encrypted_part = parts
                                        b = decrypt_data(encoded_part)
                                        cool2 = f"{b}"
                                    else:
                                        print(f"Unexpected format: {plink}\n{tid}")
                            elif data.get('ytFlag') == 1:
                                dlink = data.get('file_link')
                                if dlink:
                                    encoded_part, encrypted_part = dlink.split(':')
                                    b = decrypt_data(encoded_part)
                                    cool2 = f"{b}"
                                else:
                                    print(f"Missing video_id for {tid}")
                            else:
                                print("Unknown ytFlag value")
                            msg = f"{tid} : {cool2}\n"
                            vj += msg
                        elif type == 'PDF':
                            plink = data.get("pdf_link", "").split(':')
                            if len(plink) == 2:
                                encoded_part, encrypted_part = plink
                                vs = decrypt_data(encoded_part)
                                msg = f"{tid} : {vs}\n"
                                vj += msg
            except Exception as e:
                print(str(e))  
            vt += vj
        mm = batch_name
        cap = f"**App Name :- {name}\nBatch Name :-** `{batch_name}`"
        with open(f'{mm}.txt', 'a') as f:
            f.write(f"{vt}")
        await app.send_document(message.chat.id, document=f"{mm}.txt", caption=cap)
        await prog.delete()
        file_path = f"{mm}.txt"
        os.remove(file_path)
        await message.reply_text("Done")
    except Exception as e:
        print(str(e))
        await message.reply_text("An error occurred. Please try again later.")

@app.on_message(filters.command("rgvikramjeet"))
async def rgvikram_txt(client, message):
    global cancel
    cancel = False
    api = "apigw.rgacademy.co.in"
    name = "RG Vikramjeet"
    raw_url = f"https://{api}/post/userLogin"
    hdr = {
        "Auth-Key": "appxapi",
        "User-Id": "-2",
        "Authorization": "",
        "User_app_category": "",
        "Language": "en",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate",
        "User-Agent": "okhttp/4.9.1"
    }
    info = {"email": "", "password": ""}
    input1 = await client.ask(message.chat.id, text="Send **ID & Password** in this manner, otherwise, the bot will not respond.\n\nSend like this: **ID*Password**")
    raw_text = input1.text
    info["email"] = raw_text.split("*")[0]
    info["password"] = raw_text.split("*")[1]
    await input1.delete(True)
    scraper = cloudscraper.create_scraper()
    res = scraper.post(raw_url, data=info, headers=hdr).content
    output = json.loads(res)
    userid = output["data"]["userid"]
    token = output["data"]["token"]
    hdr1 = {
            "Host": api,
            "Client-Service": "Appx",
            "Auth-Key": "appxapi",
            "User-Id": userid,
            "Authorization": token
            }
    await message.reply_text("**login Successful**")
    res1 = requests.get(f"https://{api}/get/mycourseweb?userid="+userid, headers=hdr1)
    b_data = res1.json()['data']
    cool = ""
    for data in b_data:
        t_name = data['course_name']
        FFF = "BATCH-ID - BATCH NAME - INSTRUCTOR"
        aa = f"**`{data['id']}`      - `{data['course_name']}`**\n\n"
        if len(f'{cool}{aa}') > 4096:
            print(aa)
            cool = ""
        cool += aa
    await message.reply_text(f"**YOU HAVE THESE BATCHES:**\n\n{FFF}\n\n{cool}")
    input2 = await client.ask(message.chat.id, text="**Now send the Batch ID to Download**")
    raw_text2 = input2.text
    for data in b_data:
        if data['id'] == raw_text2:
            batch_name = data['course_name']
    scraper = cloudscraper.create_scraper()
    html = scraper.get(f"https://{api}/get/allsubjectfrmlivecourseclass?courseid={raw_text2}",headers=hdr1).content
    output0 = json.loads(html)
    subjID = output0["data"]
    fuk = ""
    for sub in subjID:
        subjid = sub["subjectid"]
        fuk += f"{subjid}&"
    prog = await message.reply_text("**Extracting Videos Links Please Wait  📥 **") 
    thread = threading.Thread(target=lambda: asyncio.run(rgvikram_down(client, message, hdr1, api, raw_text2, fuk, batch_name, name, prog)))
    thread.start()

# ---- Appex V2 Handler ----
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

# Decrypt function (reused)
def decrypt_data(encoded_data):
    try:
        key = "638udh3829162018".encode("utf8")
        iv = "fedcba9876543210".encode("utf8")
        decoded_data = b64decode(encoded_data)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(decoded_data), AES.block_size)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        raise ValueError(f"Error decrypting data: {str(e)}")

async def course_content(app, api, message, raw_text2, batch_name, name, parent_Id, hdr1):
    try:
        scraper = cloudscraper.create_scraper()
        html = scraper.get(f"https://{api}/get/folder_contentsv2?course_id={raw_text2}&parent_id={parent_Id}", headers=hdr1).content
        output = json.loads(html)
        data_list = output.get('data', [])
        vj = ""
        for data in data_list:
            try:
                if data['material_type'] == 'FOLDER':
                    id = data["id"]
                    await course_content(app, api, message, raw_text2, id, hdr1)
                elif data['material_type'] == 'VIDEO':
                    tid = data.get("Title")
                    plink = data.get("pdf_link", "").split(':')
                    if len(plink) == 2:
                        encoded_part, encrypted_part = plink
                        vs = decrypt_data(encoded_part)
                    if data.get('ytFlag') == 0:
                        dlink = next((link['path'] for link in data.get('download_links', []) if link.get('quality') == "720p"), None)
                        if dlink:
                            parts = dlink.split(':')
                            if len(parts) == 2:   
                                encoded_part, encrypted_part = parts
                                cool2 = decrypt_data(encoded_part)
                            else:
                                print(f"Unexpected format: {plink}\n{tid}")
                    elif data.get('ytFlag') == 1:
                        dlink = data.get('file_link')
                        if dlink:
                            encoded_part, encrypted_part = dlink.split(':')
                            cool2 = decrypt_data(encoded_part)
                        else:
                            print(f"Missing video_id for {tid}")
                    else:
                        print("Unknown ytFlag value")
                    msg = f"{tid} : {cool2}\n{tid} : {vs}\n"
                    vj += msg
                elif data['material_type'] == 'PDF':
                    tid = data.get("Title")
                    plink = data.get("pdf_link", "").split(':')
                    if len(plink) == 2:
                        encoded_part, encrypted_part = plink
                        vs = decrypt_data(encoded_part)
                    msg = f"{tid} : {vs}\n"
                    vj += msg
            except Exception as e:
                print(f"Error processing data: {str(e)}")
        mm = f"{batch_name}"
        cap = f"**App Name :- {name}\nBatch Name :-** `{batch_name}`"
        with open(f'{mm}.txt', 'a') as f:
            f.write(f"{vj}")
        await app.send_document(message.chat.id, document=f"{mm}.txt", caption=cap)
        file_path = f"{mm}.txt"
        os.remove(file_path)
        await message.reply_text("Done")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        await message.reply_text("An error occurred. Please try again later.")

@app.on_message(filters.command("appexv2"))
async def appex_v2_txt(client, message):
    try:
        global cancel
        cancel = False
        api = "apigw.appexams.com"
        name = "Appex V2"
        raw_url = f"https://{api}/post/userLogin"
        hdr = {
            "Auth-Key": "appxapi",
            "User-Id": "-2",
            "Authorization": "",
            "User_app_category": "",
            "Language": "en",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "okhttp/4.9.1"
        }
        info = {"email": "", "password": ""}
        input1 = await client.ask(message.chat.id, text="Send **ID & Password** in this manner, otherwise, the bot will not respond.\n\nSend like this: **ID*Password**")
        raw_text = input1.text
        info["email"] = raw_text.split("*")[0]
        info["password"] = raw_text.split("*")[1]
        await input1.delete(True)
        scraper = cloudscraper.create_scraper()
        res = scraper.post(raw_url, data=info, headers=hdr).content
        output = json.loads(res)
        userid = output["data"]["userid"]
        token = output["data"]["token"]
        hdr1 = {
                "Host": api,
                "Client-Service": "Appx",
                "Auth-Key": "appxapi",
                "User-Id": userid,
                "Authorization": token
                }
        await message.reply_text("**login Successful**")
        res1 = requests.get(f"https://{api}/get/get_all_purchases?userid="+userid+"&item_type=10", headers=hdr1)
        b_data = res1.json().get('data', [])
        FFF = "BATCH-ID - BATCH NAME\n\n"
        for data in b_data:
            cdatas = data['coursedt']
            for cdata in cdatas:      
                FFF += f"**`{cdata['id']}`      - `{cdata['course_name']}`**\n\n"
        await message.reply_text(f"**YOU HAVE THESE BATCHES:\n\n{FFF}")
        input2 = await client.ask(message.chat.id, text="**Now send the Batch ID to Download**")
        raw_text2 = input2.text
        for data in b_data:
            cdatas = data['coursedt']
            for cdata in cdatas:      
                if cdata['id'] == raw_text2:
                    batch_name = cdata['course_name']
        scraper = cloudscraper.create_scraper()
        html = scraper.get(f"https://{api}/get/folder_contentsv2?course_id={raw_text2}&parent_id=-1", headers=hdr1).content
        output0 = json.loads(html)
        parent_Id = output0['data'][0]['id']
        await course_content(client, api, message, raw_text2, batch_name, name, parent_Id, hdr1)
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        await message.reply_text("An error occurred. Please try again later.")

# ---- Appex V3 Handler ----
import threading
import cloudscraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from base64 import b64decode

def decrypt_data(encoded_data):
    try:
        key = "638udh3829162018".encode("utf8")
        iv = "fedcba9876543210".encode("utf8")
        decoded_data = b64decode(encoded_data)
        cipher = AES.new(key, AES.MODE_CBC, iv)
        decrypted_data = unpad(cipher.decrypt(decoded_data), AES.block_size)
        return decrypted_data.decode('utf-8')
    except Exception as e:
        print(f"Decryption error: {e}")
        return ""

async def appex_down(app, message, hdr1, api, raw_text2, fuk, batch_name, name, prog):
    vt = ""
    try:
        subject_ids = fuk.split('&')
        for subject_id in subject_ids:
            if not subject_id:
                continue
            res3 = requests.get(f"https://{api}/get/alltopicfrmlivecourseclass?courseid={raw_text2}&subjectid={subject_id}", headers=hdr1)
            topics = res3.json().get('data', [])
            vj = ""
            for topic in topics:
                topic_id = topic.get("topicid")
                if not topic_id:
                    continue
                res4 = requests.get(f"https://{api}/get/livecourseclassbycoursesubtopconceptapiv3?topicid={topic_id}&start=-1&courseid={raw_text2}&subjectid={subject_id}", headers=hdr1).json()
                materials = res4.get("data", [])
                for material in materials:
                    title = material.get("Title", "No Title")
                    material_type = material.get('material_type')
                    video_link = ""
                    pdf_link = ""
                    if material_type == 'VIDEO':
                        if material.get('ytFlag') == 0 and material.get('ytFlagWeb') == 0:
                            dlink = next((link['path'] for link in material.get('download_links', []) if link.get('quality') == "720p"), None)
                            if dlink:
                                parts = dlink.split(':')
                                if len(parts) == 2:   
                                    encoded_part, encrypted_part = parts
                                    b = decrypt_data(encoded_part)
                                    cool2 = f"{b}"
                                else:
                                    print(f"Unexpected format: {plink}\n{tid}")
                        elif material.get('ytFlag') == 1:
                            dlink = material.get('file_link')
                            if dlink:
                                encoded_part, encrypted_part = dlink.split(':')
                                video_id = decrypt_data(encoded_part).split('/')[-1]
                                video_link = f"https://youtu.be/{video_id}"
                            else:
                                print(f"No YouTube link found for video {title}")
                        vj += f"{title} : {video_link}\n"
                    elif material_type == 'PDF':
                        plink = material.get("pdf_link", "").split(':')
                        if len(plink) == 2:
                            encoded_part, encrypted_part = plink
                            pdf_link = decrypt_data(encoded_part)
                        vj += f"{title} : {pdf_link}\n"
            vt += vj
        mm = batch_name
        cap = f"**App Name :- {name}\nBatch Name :-** `{batch_name}`"
        with open(f'{mm}.txt', 'a') as f:
            f.write(f"{vt}")
        await app.send_document(message.chat.id, document=f"{mm}.txt", caption=cap)
        await prog.delete()
        file_path = f"{mm}.txt"
        os.remove(file_path)
        await message.reply_text("Done")
    except Exception as e:
        print(str(e))
        await message.reply_text("An error occurred. Please try again later.")

@app.on_message(filters.command("appexv3"))
async def appex_v3_txt(client, message):
    global cancel
    cancel = False
    token = ""
    api = "apigw.appexams.com"
    name = "Appex V3"
    input1 = await client.ask(message.chat.id, text="Send **Token**. If you don’t have one, type `NO` to login with ID & Password.")
    token_text = input1.text
    if token_text.strip().upper() != "NO":
        token = token_text
    else:
        raw_url = f"https://{api}/post/userLogin"
        hdr = {
            "Auth-Key": "appxapi",
            "User-Id": "-2",
            "Authorization": "",
            "User_app_category": "",
            "Language": "en",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate",
            "User-Agent": "okhttp/4.9.1"
        }
        info = {"email": "", "password": ""}
        input2 = await client.ask(message.chat.id, text="Send **ID & Password** in this manner, otherwise, the bot will not respond.\n\nSend like this: **ID*Password**")
        raw_text = input2.text
        info["email"] = raw_text.split("*")[0]
        info["password"] = raw_text.split("*")[1]
        await input2.delete(True)
        scraper = cloudscraper.create_scraper()
        res = scraper.post(raw_url, data=info, headers=hdr).content
        output = json.loads(res)
        token = output["data"]["token"]
    await message.reply_text("**Login Successful**")
    hdr1 = {
        "Host": api,
        "Client-Service": "Appx",
        "Auth-Key": "appxapi",
        "User-Id": token if token else "-2",
        "Authorization": token
    }
    res1 = requests.get(f"https://{api}/get/mycourseweb?userid={token}", headers=hdr1)
    b_data = res1.json()['data']
    cool = ""
    for data in b_data:
        t_name = data['course_name']
        FFF = "BATCH-ID - BATCH NAME - INSTRUCTOR"
        aa = f"**`{data['id']}`      - `{data['course_name']}`**\n\n"
        if len(f'{cool}{aa}') > 4096:
            print(aa)
            cool = ""
        cool += aa
    await message.reply_text(f"**YOU HAVE THESE BATCHES:**\n\n{FFF}\n\n{cool}")
    input3 = await client.ask(message.chat.id, text="**Now send the Batch ID to Download**")
    raw_text2 = input3.text
    for data in b_data:
        if data['id'] == raw_text2:
            batch_name = data['course_name']
    scraper = cloudscraper.create_scraper()
    html = scraper.get(f"https://{api}/get/allsubjectfrmlivecourseclass?courseid={raw_text2}", headers=hdr1).content
    output0 = json.loads(html)
    subjID = output0["data"]
    fuk = "&".join([sub["subjectid"] for sub in subjID if "subjectid" in sub])
    prog = await message.reply_text("**Extracting Videos Links Please Wait  📥 **") 
    thread = threading.Thread(target=lambda: asyncio.run(appex_down(client, message, hdr1, api, raw_text2, fuk, batch_name, name, prog)))
    thread.start()

app.run()
