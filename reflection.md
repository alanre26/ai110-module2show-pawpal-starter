# PawPal+ Project Reflection

## 1. System Design
A user should be able to add a pet as well as multiple pets, their choice of pets 

User should be able to scedule daily or weekly walks, for most dog walkers its around the same time everyday. in the morning and possibly noon 

A user should be able to see a calendar view of todays task with time and be able to check off tasks.

a user should be able to edit modify and delete all of them 

**a. Initial design**

- Briefly describe your initial UML design.
The inital design stems from class schedule and then followed by owner then pet and then task. pointing from the top down. all carry attributes.

- What classes did you include, and what responsibilities did you assign to each?
I included 4 classes, they are Scheduler, Owner, Pet, Task. For Scheduler a responbility given was fetch todays tasks, as well as sort by priority. For owner it has responbility of adding pets and setting available minutes. Pet class has responsiblities of completeing task and editing tasks. Task class has assigned priority, preferred time, completed or not, and frequency.


**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.
Yes, one change im going to make is a task doesnt know which pet its assigned too, as well as AI help me uncover that task ids are ambigious. If i remove task_id=1 that can remove it for both pets with the same task.
Another change needed is currently bool is set tp true forever if task is done, but for recurring tasks it should be set off again for owner to check it again for the next day
Later on i ended up changing how recurring tasks work. Now when you finish a daily or weekly task it makes a brand new copy of the task for the next day (or next week) instead of resetting the same one. that way each task is just one day and you can see what was actually done.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
The scheduler looks at how many minutes the owner has free today, the priority of each task (high, medium, low), the preferred time of the task if it has one, and the frequency so it knows whats actually due today (daily, weekly on a certain day, or once).

- How did you decide which constraints mattered most?
Time and priority mattered most. A owner only has so much time in the day and stuff like feeding and meds cant get skipped, but grooming or brushing can wait till tomorrow. So high priority goes first, and if two tasks are the same priority the shorter one goes first so more stuff fits. Preferred time is mostly used to put the plan in order and to catch conflicts.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
The scheduler picks tasks by priority and just checks if the minutes add up. It doesnt actually move tasks around into open time slots, so if two tasks overlap it just gives a warning instead of fixing it. For example Dinner for Mochi and Litter box for Luna both at 6pm both get scheduled and you get a "Owner is double-booked" warning.

- Why is that tradeoff reasonable for this scenario?
For a pet owner its reasonable because the owner knows their day better then the app does. Sometimes two things at the same time is fine (feeding the cat while the dog eats) and sometimes its not, so a warning lets them decide. It also keeps the code simple and the program never crashes because of a conflict.

Another smaller tradeoff is conflict detection only checks tasks that have a set time. "Anytime" tasks like brushing never get flagged because the scheduler doesnt know when they'll happen. It does check overlapping durations though and not just exact same start times, so a 12:10 medication during a 12:00-12:20 walk still gets caught.

- Readability vs "pythonic"
When i asked the AI how to simplify my algorithms it gave me two ideas. For detect_conflicts it showed a shorter version using itertools.combinations to compare every pair of tasks. It was more "pythonic" but harder to follow and it checks every single pair, while mine sorts first and stops looking once the next task starts after the current one ends. So i kept mine. For filter_tasks i did take the simpler version, it went from one big and/or condition to filtering one step at a time (pet first, then done or not done), which is way easier to read and works the same.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used AI for pretty much every part. brainstorming the UML and classes, figuring out that task ids were ambigious between pets, adding docstrings, writing tests, and planning the algorithms in phase 3 (sorting, filtering, recurring tasks, conflicts). It also found a bug where a weekly task with no day set would come back every single day after you finished it.

- What kinds of prompts or questions were most helpful?
The most helpful was giving it my actual files and the assignment step and asking for a list of small improvements, instead of asking it to just write everything. Asking "how" questions also helped, like how to use a lambda as a key in sorted() for "HH:MM" times and how to use timedelta to get tomorrows date. That way i understood it and wasnt just copying.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
For recurring tasks the AI first said i should keep one task object and just track the last date it was completed. But the assignment wanted a new task to be created for the next occurrence, so i went with that instead. Also one time the AI changed main.py to grab a task by its position in the list and it crashed with an IndexError because Luna only had 3 tasks, so that had to get fixed.

- How did you evaluate or verify what the AI suggested?
I ran main.py after every change and actually read the output to see if it made sense, like checking the 6pm tasks showed a conflict and that the weekly grooming came back 7 days later and not the next day. I also ran pytest to make sure the tests all passed.

**c. AI Strategy**

- Which AI coding assistant features were most effective for building your scheduler?
Letting it read my actual files and run things itself. It would run pytest and main.py after making changes so i could see right away if something broke, and for the streamlit app it clicked through the UI in a test to make sure the new buttons worked. Asking it to explain code before i saved it helped too.

- Give one example of an AI suggestion you rejected or modified to keep your system design clean.
The itertools.combinations version of detect_conflicts. It was shorter but it checks every pair of tasks and was harder for me to follow, so i kept my version that sorts first and stops early.

- How did using separate chat sessions for different phases help you stay organized?
Each chat only had to deal with one thing, like testing or the UI, so the AI didnt get mixed up with older stuff and its answers stayed focused. It also made it easier for me to go back and find what was decided in each phase.

- Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.
The AI can write a lot of code fast but i still have to decide how the classes fit together and what the app should actually do. My job was more about saying what i wanted, checking what it gave me, and saying no when it didnt fit the design.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
Marking a task complete, adding a task to a pet, sorting tasks by time with the "anytime" ones at the end, filtering by pet and by done/not done, a daily task making a new copy for tomorrow, a weekly task making a copy for 7 days later, once tasks not repeating, completing the same task twice not making duplicates, overlapping tasks giving a warning, and back to back tasks (8:00-8:30 then 8:30) NOT giving a warning. Later i added edge cases too, like a pet with no tasks, two tasks at the exact same time, two different pets clashing, and a task that got missed staying on the list until its done.

- Why were these tests important?
These are the parts a owner would actually depend on. If recurring tasks are wrong the owner either forgets to feed their pet or sees the same task twice. The back to back test was important because its an easy off by one mistake and i didnt want fake warnings all over the schedule.

**b. Confidence**

- How confident are you that your scheduler works correctly?
Pretty confident, like a 4 out of 5. All 16 tests pass and the demo output looks right, but the tests only cover the cases i thought of and the streamlit app isnt tested automatically.

- What edge cases would you test next if you had more time?
A task that goes past midnight (like 11:45pm for 30 min), what happens if you undo a completed task since the next copy still exists, old copies piling up if the owner doesnt check things off for a while, and a owner with 0 minutes free.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I like the conflict warnings and how the schedule prints out in the terminal. It tells you if the same pet is double booked or if you as the owner are trying to be in two places at once, which feels like something a real pet owner would actually want.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would make the scheduler actually move tasks into open time slots instead of just warning about them, and put "anytime" tasks into gaps in the day. I would also save the pets and tasks to a file so they dont disappear when the streamlit app restarts.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
AI is really fast at writing code but i still had to run it and check it myself. It made mistakes sometimes and it doesnt always know what the assignment wants, so i had to make the design decisions and use it more like a helper then something that does everything.
