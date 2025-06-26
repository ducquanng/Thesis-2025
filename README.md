# Thesis-2025
AI-driven sales process (Team 20)

**MKB Marketing Email Generator**

<ins>What does this tool do?</ins>
The Marketing Email Generator is a simple app that helps MKB account managers quickly create personalized email invitations. It automatically generates personalized invitations for innovation challenges for Dutch SMEs, using the name of the selected challenge and the company. In other words, you pick a challenge (a project run by a knowledge institution) and a company name, and the tool drafts a cold-recruitment email for that company. This saves you time when reaching out to many businesses and ensures each email mentions the right challenge details.


<ins>Who is it for?</ins>
This tool is designed for MKB account managers and marketing staff who invite small and medium-sized enterprises (SMEs) to participate in innovation projects. It makes writing each email faster while still including personalized, relevant content.

<ins>How does it work (simplified)?</ins>
-	Pulls challenge info: The tool looks up the selected innovation challenge in a prepared Excel database. This database contains all the project details (like challenge descriptions).
-	Uses AI (GPT-4): It then uses a smart language model (GPT-4) behind the scenes. The model is given the challenge info and the company name, and it writes the draft email.
-	Combines details into an email: The output is an email with a subject line and body, structured to grab attention and explain the opportunity. 
-	Fully personalized: Because it knows the company name and challenge details, the email feels tailored to that SME. In short, it finds relevant facts about the challenge and asks GPT-4 to generate a customized, persuasive email.

All of this happens automatically when you press "Generate Email". You don’t need to write the email yourself – just review the draft when it appears.

<ins>What do I need to run the tool?</ins>
-	Computer with the tool installed: The app runs locally using Streamlit. You will need the file core.py and interface.py locally on your device. After that just launch the app when you want to use it.
-	Challenge Excel file: You need an Excel file (.xlsx) containing the project/challenge data. This file should have each challenge listed in rows, with columns like Challenge Name, Description, etc. Think of it as a spreadsheet database of all current projects.
-	Internet/API access for AI: The tool uses the OpenAI GPT-4 model. This usually means an active internet connection. As a user, you just need to make sure the app can connect to the LLM.


<ins>Final remarks on the generated email draft:</ins>
-	Always check the email before sending: The AI does its best, but it can vary the wording each time. Double-check that the company name, challenge details, and tone look right. Make sure nothing important was misunderstood or missed.
-	Format: The draft follows a clear structure (attention-grabbing intro, brief challenge summary, benefits to the SME, and a call to action). It uses simple, friendly language. All text will be in Dutch to match the SME’s language.
-	Multiple tries: If you want a different style, you can regenerate the email (often it will come out slightly differently each time). Use the version you like best.
-	Update data: If there’s new information about a challenge (or new challenges), update the Excel file and re-upload it. The app will then use the latest data for new emails.

By using this tool, you can save time writing each individual email. It keeps the outreach personal and relevant, which helps get better responses when recruiting SMEs for MKB Werkplaats projects.
