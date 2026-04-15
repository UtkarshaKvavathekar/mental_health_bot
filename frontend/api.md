# Dashboard API

GET /dashboard/{user_id}

Response:
{
  "name": "string",
  "meditationMinutes": number,
  "chatMessages": number,
  "streak": number,
  "moodHistory": [
    { "day": "Mon", "value": 60 }
  ],
  "todayFocus": "string",
  "focusTip": "string",
  "insight": "string"
}

-------------------------------------

# Save Mood

POST /mood

Request:
{
  "user_id": "string",
  "mood": "😊"
}

# History API

GET /history/{user_id}

Response:
{
  "totalSessions": number,
  "totalMinutes": number,
  "streak": number,
  "sessions": [
    {
      "date": "2026-04-10",
      "exercise": "Breathing",
      "duration": 10
    }
  ]
}

-------------------------------------

DELETE /history/{user_id}

# Profile API

GET /profile/{user_id}

Response:
{
  "id": "string",
  "name": "string",
  "email": "string",
  "memberSince": "Jan 2024",

  "messagesSent": number,
  "meditationSessions": number,
  "totalMeditationTime": number,
  "streak": number,
  "moodEntries": number,
  "daysUsingApp": number,

  "moodHistory": [
    { "day": "Mon", "value": 70 }
  ]
}

{
  "id": "string",
  "name": "string",
  "email": "string",
  "memberSince": "Jan 2024",

  "messagesSent": number,
  "meditationSessions": number,
  "totalMeditationTime": number,
  "streak": number,
  "moodEntries": number,
  "daysUsingApp": number,

  "moodHistory": [
    { "day": "Mon", "value": 70 }
  ],

  "recentMeditations": [
    {
      "exercise": "Body Scan",
      "time": "Today, 10:30 AM",
      "duration": 15,
      "moodBefore": "😔",
      "moodAfter": "😊"
    }
  ]
}


# Chat API

POST /chat

Request:
{
  "user_id": "string",
  "message": "string"
}

Response:
{
  "reply": "string"
}


# 🧘 Meditation API

## 1. Save Meditation Session

POST /meditation

Request:
{
"user_id": "string",
"exercise": "string",
"duration": number,
"date": "YYYY-MM-DD",
"startMood": "string (optional)",
"endMood": "string (optional)"
}

Response:
{
"message": "Meditation session saved successfully",
"updatedStreak": number
}

---

## 2. Get Meditation Dashboard Summary

GET /meditation/summary/{user_id}

Response:
{
"totalSessions": number,
"totalMinutes": number,
"currentStreak": number,
"weeklyProgress": [
{ "day": "Mon", "minutes": 10 }
]
}

---

## 3. Get Meditation History

GET /meditation/history/{user_id}

Response:
{
"sessions": [
{
"date": "2026-04-10",
"exercise": "4-7-8 Breathing",
"duration": 10,
"moodBefore": "😔",
"moodAfter": "😊"
}
]
}

---

## 4. Delete Meditation History

DELETE /meditation/history/{user_id}

Response:
{
"message": "History cleared successfully"
}
