!pip install python-telegram-bot==13.7 scikit-learn pandas spacy
!python -m spacy download en_core_web_sm


from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove

# Expanded symptom list
SYMPTOMS = [
    "fever", "cough", "headache", "fatigue", "sore_throat", "nausea", "vomiting", "diarrhea", 
    "chills", "muscle_pain", "joint_pain", "shortness_breath", "chest_pain", "dizziness", 
    "rash", "sweating", "loss_appetite", "weight_loss", "abdominal_pain", "back_pain", 
    "runny_nose", "sneezing", "congestion", "itchy_eyes", "ear_pain", "hearing_loss", 
    "vision_blur", "dry_mouth", "thirst", "frequent_urination", "swelling", "bruising", 
    "bleeding", "palpitations", "anxiety", "depression", "insomnia", "confusion", 
    "memory_loss", "tremors", "numbness", "tingling", "weakness", "seizures", 
    "difficulty_swallowing", "hoarseness", "hair_loss", "skin_dryness", "fainting",
    "night_sweats", "swollen_lymph_nodes", "jaundice", "bloody_stool", "wheezing", 
    "loss_of_smell", "joint_stiffness", "chest_tightness", "sensitivity_to_light", 
    "unexplained_fever", "persistent_cough"
]

# Expanded rule-based disease prediction
def predict_condition(selected_symptoms):
    symptoms_set = set(selected_symptoms)
    
    # Rules for diseases
    if {"fever", "cough", "fatigue", "muscle_pain"}.issubset(symptoms_set):
        return "flu", "You might have the flu. Rest, stay hydrated, and see a doctor if symptoms worsen."
    elif {"runny_nose", "sneezing", "sore_throat"}.issubset(symptoms_set):
        return "cold", "It could be a cold. Gargle salt water and get plenty of rest."
    elif {"headache", "vision_blur", "sensitivity_to_light"}.issubset(symptoms_set):
        return "migraine", "You may have a migraine. Avoid bright lights and rest in a quiet place."
    elif {"cough", "shortness_breath", "chest_pain", "fever"}.issubset(symptoms_set):
        return "pneumonia", "Possible pneumonia. Seek medical attention immediately."
    elif {"nausea", "vomiting", "diarrhea", "abdominal_pain"}.issubset(symptoms_set):
        return "gastroenteritis", "Likely gastroenteritis. Stay hydrated and avoid solid food for now."
    elif {"anxiety", "palpitations", "insomnia"}.issubset(symptoms_set):
        return "anxiety_disorder", "You might be experiencing anxiety. Try deep breathing or consult a specialist."
    elif {"thirst", "frequent_urination", "fatigue"}.issubset(symptoms_set):
        return "diabetes", "Possible diabetes symptoms. Monitor your blood sugar and see a doctor."
    elif {"chest_pain", "palpitations", "headache"}.issubset(symptoms_set):
        return "hypertension", "Could be hypertension. Check your blood pressure and consult a professional."
    elif {"itchy_eyes", "sneezing", "rash"}.issubset(symptoms_set):
        return "allergy", "It might be an allergy. Avoid triggers and consider an antihistamine."
    elif {"persistent_cough", "night_sweats", "weight_loss", "fever"}.issubset(symptoms_set):
        return "tuberculosis", "Possible tuberculosis. Seek medical attention urgently."
    elif {"jaundice", "nausea", "fatigue", "abdominal_pain"}.issubset(symptoms_set):
        return "hepatitis", "You might have hepatitis. Consult a doctor for liver function tests."
    elif {"wheezing", "shortness_breath", "chest_tightness"}.issubset(symptoms_set):
        return "asthma", "Could be asthma. Use an inhaler if available and see a doctor."
    elif {"swollen_lymph_nodes", "night_sweats", "unexplained_fever", "weight_loss"}.issubset(symptoms_set):
        return "lymphoma", "Possible lymphoma. Seek medical evaluation immediately."
    elif {"fever", "cough", "loss_of_smell", "fatigue"}.issubset(symptoms_set):
        return "COVID-19", "You might have COVID-19. Isolate and get tested as soon as possible."
    elif {"joint_pain", "joint_stiffness", "swelling"}.issubset(symptoms_set):
        return "arthritis", "Could be arthritis. Rest the joint and consult a doctor."
    else:
        return "unknown", "This might be a rare disease. Please contact a doctor."

# Conversation states
SELECTING_SYMPTOMS, CONFIRMING = range(2)

# Telegram bot handlers
def start(update, context):
    context.user_data["selected_symptoms"] = []
    symptom_keyboard = [SYMPTOMS[i:i+5] for i in range(0, len(SYMPTOMS), 5)]  # 5 symptoms per row
    symptom_keyboard.append(["Done"])
    reply_markup = ReplyKeyboardMarkup(symptom_keyboard, one_time_keyboard=False)
    update.message.reply_text(
        "Hi! I’m your Healthcare Chatbot. Please select your symptoms one by one. When finished, press 'Done'.",
        reply_markup=reply_markup
    )
    return SELECTING_SYMPTOMS

def select_symptom(update, context):
    user_input = update.message.text
    if user_input == "Done":
        symptoms = context.user_data["selected_symptoms"]
        if not symptoms:
            update.message.reply_text("You haven’t selected any symptoms. Please select at least one or type /cancel.")
            return SELECTING_SYMPTOMS
        update.message.reply_text(
            f"You selected: {', '.join(symptoms)}. Is this correct? (Yes/No)",
            reply_markup=ReplyKeyboardMarkup([["Yes", "No"]], one_time_keyboard=True)
        )
        return CONFIRMING
    elif user_input in SYMPTOMS:
        if user_input not in context.user_data["selected_symptoms"]:
            context.user_data["selected_symptoms"].append(user_input)
            update.message.reply_text(f"Added '{user_input}'. Select another symptom or press 'Done'.")
        else:
            update.message.reply_text(f"'{user_input}' is already selected. Choose another or press 'Done'.")
    else:
        update.message.reply_text("Invalid symptom. Please select from the list or press 'Done'.")
    return SELECTING_SYMPTOMS

def confirm_symptoms(update, context):
    user_input = update.message.text
    if user_input == "Yes":
        symptoms = context.user_data["selected_symptoms"]
        condition, response = predict_condition(symptoms)
        update.message.reply_text(
            f"Based on {symptoms}, {response}",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    elif user_input == "No":
        context.user_data["selected_symptoms"] = []
        symptom_keyboard = [SYMPTOMS[i:i+5] for i in range(0, len(SYMPTOMS), 5)]
        symptom_keyboard.append(["Done"])
        update.message.reply_text(
            "Let’s start over. Please select your symptoms again.",
            reply_markup=ReplyKeyboardMarkup(symptom_keyboard, one_time_keyboard=False)
        )
        return SELECTING_SYMPTOMS
    else:
        update.message.reply_text("Please reply with 'Yes' or 'No'.")
        return CONFIRMING

def cancel(update, context):
    update.message.reply_text("Operation cancelled. Type /start to begin again.", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

# Main function to run the bot
def main():
    updater = Updater("7501316881:AAG1KFyRKapr6eR43DwasENa0pbmWRThdkA", use_context=True)  # Replace with your token
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_SYMPTOMS: [MessageHandler(Filters.text & ~Filters.command, select_symptom)],
            CONFIRMING: [MessageHandler(Filters.text & ~Filters.command, confirm_symptoms)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )
    
    dp = updater.dispatcher
    dp.add_handler(conv_handler)
    
    updater.start_polling()
    print("Bot is running...")
    updater.idle()

if __name__ == "__main__":
    main()
