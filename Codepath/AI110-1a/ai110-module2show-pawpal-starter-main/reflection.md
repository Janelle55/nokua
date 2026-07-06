# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
 The initial UML design has four classes, one for the owner information, pet information, tasks, and then one to generate a final schedule.
 
- What classes did you include, and what responsibilities did you assign to each?
For the owner class, there should be basic information such as name, age, and preferences. Likewise, the pet class functions in a similar manner. The task class should describe and manage tasks, and the scheduler class should create a personalized schedule.

**b. Design changes**

- Did your design change during implementation?
Yes, my design changed a little once I started building it out. I did not really see the gaps until I tried to make the scheduler actually work.

- If yes, describe at least one change and why you made it.

The main change I made was adding a link from each task back to the pet it belongs to. At first my design only went one way, from the owner to the pet to the task. When I worked on the conflict checker I realized it could not tell me which pet a task was for. A message that just says two tasks overlap is not very helpful, so I wanted it to say something like Rex's walk overlaps with Bella's task instead.

I also changed how priority works. I first had it as a plain word like high or low, but when I tried to sort by priority the words sorted in alphabetical order, which put them in the wrong order. So I gave priority a number ranking instead so it sorts the way I expect. I kept the time as simple HH:MM text so it still matches my diagram, but I added a small helper that turns it into minutes, so the scheduler can actually do the math to check if two tasks overlap.

One more change was letting the scheduler get all the tasks through the owner instead of digging through every pet again in each method. That keeps the code in one place and is easier to follow.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
My scheduler looks at the time a task starts and how long it takes, the priority level, and how often the task repeats. It also keeps track of whether a task is already done, so finished tasks do not show up in the plan or cause fake conflicts.

- How did you decide which constraints mattered most?
Time mattered the most to me because the whole point is to know when things happen during the day, and time is what makes two tasks bump into each other. Priority came next since a busy owner needs to know which task is more important if they run out of time. I left owner preferences out for now so I could get the main logic working first.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
One tradeoff is in how I check for conflicts. I decided to check if the time windows actually overlap instead of only checking if two tasks start at the exact same time. To do that I compare every pair of tasks, which is not the fastest way to do it. I also keep the time as simple text, so it does not handle a task that goes past midnight.

- Why is that tradeoff reasonable for this scenario?
A pet owner only has a handful of tasks in a day, not thousands, so checking every pair still runs instantly and is easy to read and trust. Checking for real overlaps is also more correct, since a 30 minute walk at 8:00 really does clash with something at 8:15, not just something else at 8:00. Tasks that cross midnight are pretty rare for daily pet care, so I felt okay leaving that out for now.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
I used my AI assistant through most of the project. It helped me turn my notes into a UML diagram, set up the class skeletons, and then fill in the actual code, the tests, and the Streamlit part. I also had it review my skeleton and point out relationships I was missing before I wrote the real logic. The most useful part was having it run my demo and my tests in the terminal so I could actually see the output instead of guessing.

- What kinds of prompts or questions were most helpful?
Being specific helped the most. Questions like how should the scheduler get all the tasks from the owner's pets, or how do I check for conflicts without crashing the program, worked a lot better than just asking it to build the whole thing at once.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
At one point the AI put a warning emoji inside the conflict messages. When I ran the demo, my terminal on Windows crashed because it could not print that emoji. So I changed the terminal version to use a plain marker instead and only kept the nicer emoji in the app itself. I also pushed back on keeping priority as plain text, since that would have sorted my tasks in the wrong order.

- How did you evaluate or verify what the AI suggested?
I checked things by actually running them instead of just trusting the code. I ran the demo file and the tests after changes to make sure everything still worked. When the emoji crash happened, the error message showed me exactly where the problem was, and I ran it again after the fix to make sure it finished cleanly.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I wrote tests for the main things the app depends on. I checked that marking a task complete changes its status, that adding a task to a pet increases the count, that tasks sort correctly by time and by priority, that filtering by pet and by status works, that overlapping tasks get flagged but back to back tasks do not, and that finishing a daily or weekly task creates the next one. I also tested a couple of edge cases, like a pet with no tasks.

- Why were these tests important?
These are the parts that the whole plan depends on. If the sorting or the conflict check is wrong, the schedule would give the owner bad information, which is worse than having nothing. The back to back test mattered a lot because that is the tricky line between a real overlap and tasks that just touch.

**b. Confidence**

- How confident are you that your scheduler works correctly?
Pretty confident, around a 4 out of 5. All of my tests pass and they cover both the normal cases and the tricky ones. I am not at a full 5 because my time is still just text, so I have not handled things like a task that goes past midnight or someone typing in a bad time.

- What edge cases would you test next if you had more time?
I would test tasks that cross midnight, bad time input like 25:00, three or more tasks overlapping at once, and I would lock the date in my tests so the recurring task tests always give the same result no matter what day I run them.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
I am most happy with getting the conflict checking and the repeating tasks to work together, and with testing the logic in the terminal before building the app. By the time I connected everything to Streamlit, the hard part was already working, so the app part was mostly just hooking it up.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
I would switch the time from plain text to a real time type so things like midnight and bad input are handled for me. I would also add owner preferences as a real setting, like no tasks before 7 in the morning, and give repeating tasks an end date so they do not keep going forever.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
The biggest thing I learned is that I am the one in charge of the design, and the AI is more like a fast helper. It writes code quickly and catches things I miss, but it will also give me something that looks right but is actually wrong, like the priority sorting or the emoji that crashed my terminal. Keeping separate chats for each part helped me stay organized, and actually running the code myself is what caught the real problems.
