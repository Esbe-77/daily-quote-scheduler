import smtplib
import json
import random
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import date, datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Settings ─────────────────────────────────────────────────────────────────
JSON_FILE   = "stoic_quotes.json"
NUM_QUOTES  = 1
DECAY_WEEKS = 4
SMTP_HOST   = "smtp.gmail.com"
SMTP_PORT   = 587

EMAIL_ADDRESS  = os.getenv("EMAIL_SENDER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
EMAIL_RECEIVER = os.getenv("EMAIL_RECEIVER")

# ── RSS feeds ─────────────────────────────────────────────────────────────────
FINANCE_FEEDS = [
    "https://feeds.reuters.com/reuters/businessNews",
    "https://feeds.reuters.com/reuters/companyNews",
    "https://www.ft.com/?format=rss",
]

TECH_FEEDS = [
    "https://feeds.arstechnica.com/arstechnica/technology-lab",
    "https://feeds.feedburner.com/TechCrunch",
    "https://www.theverge.com/rss/index.xml",
]

# ── Philosophical readings (rotated daily) ───────────────────────────────────
PASSAGES = [
    ("On the Present Moment", "Marcus Aurelius",
"""Marcus Aurelius was the most powerful man in the world, yet he spent his mornings writing reminders to himself. The Meditations were never intended for publication — they are private notes, exercises in self-correction, written by a man who knew how easy it is to forget what actually matters.

His recurring theme was the present moment. Not the past, which cannot be changed, nor the future, which has not arrived — but this, here, now. Most of our distress, he observed, comes not from events but from our judgments about them. We do not simply experience difficulty; we tell ourselves stories about it. Strip the story away and what remains is a situation requiring a response.

The practice he recommended was deceptively simple: whenever something unsettles you, ask what part of it is actually within your control. Your effort, your attention, your values, your response — these are yours. The outcome, other people's reactions, the weather of circumstance — these are not. Once you have sorted what is yours from what is not, spend your energy only on the first list.

This is not passivity. Aurelius was also a general who spent years on military campaign. The point is not to stop caring, but to stop spending your present moment on things that are not your present moment's work. Grief for the past and anxiety about the future are forms of time theft — they take the only resource you actually have and spend it on things that cannot receive it.

Time, he wrote, is a river of disappearing moments. Every one of them is, in some sense, a new life. The man who will begin tomorrow is gambling with the only morning he is sure of.

What makes the Meditations worth returning to is their honesty. Aurelius is not lecturing a student; he is talking to himself, in the dark, at the start of another difficult day. He does not claim to have mastered these ideas — only that they are worth practising. That is the right way to hold them."""),

    ("On the Shortness of Life", "Seneca",
"""Life is not short. We make it short by the way we use it.

This is the central argument Seneca pressed on his friend Lucilius across the letters that would make him one of antiquity's most readable thinkers. 'It is not that we have a short time to live,' he wrote, 'but that we waste a good deal of it. Life is long enough, and a sufficiently generous amount has been given to us for the highest achievements — if it were all well invested.'

Look at how people spend their days. Years given to ambition — accumulating titles, chasing reputation, currying favour with the powerful. Years given to distraction — the business of being busy, filling every hour so there is no space to ask what it is all for. The truly busy person, in Seneca's view, is the most impoverished. They have traded time — the only currency that cannot be replaced — for things that could have waited or did not matter.

What he recommended was not idleness but intentionality. Choose what you give your hours to. Reclaim some portion of each day for thought, for real conversation, for the kind of reading that changes how you see. 'Omnia aliena sunt,' he wrote — all other things are external, borrowed. Only time is truly ours, and we guard it with far less care than we guard our money.

Seneca was in his sixties when he wrote these letters. He had survived exile, served a dangerous emperor, and wasted years he freely admitted could have been better spent. The urgency in his writing is not anxiety — it is someone shaking you gently by the shoulder.

You are not going to live forever. The morning you are reading this is one of a finite number of mornings. That is not a reason for despair. It is a reason to begin."""),

    ("On What We Control", "Epictetus",
"""Epictetus was born a slave. He had no control over where he lived, who owned him, or what was done to him. And yet he became one of antiquity's most influential philosophers, precisely because he thought harder than almost anyone else about what freedom actually means.

His answer was radical and remains so: freedom is not the absence of external constraint. It is the recognition of which things are genuinely yours and which are not.

He divided everything into two categories. In our power: judgment, desire, aversion, and in general whatever is our own action. Not in our power: body, reputation, office, property — whatever is not our own action. The reason most people are unhappy, he argued, is that they have mixed up the two lists. They treat their reputation as theirs, and suffer when others judge them poorly. They treat their health as theirs, and are undone by illness. None of these things were ever fully in their control. The suffering comes not from losing them but from having confused them for something they owned.

What you actually own is how you respond. Your interpretation of an event. Your values, held or abandoned. Your attention, given here or there. These are genuinely yours — no one can take them without your consent.

This sounds cold, but Epictetus did not mean it coldly. He wept at the difficulties of his students. He insisted on compassion, engagement with the world, love for others. The point was not detachment but accurate accounting. Know what is yours, protect it fiercely, and hold everything else lightly enough that it does not take you down when it goes.

The test he recommended was simple: before you are troubled by something, ask whether it is in your control. If it is, act. If it is not, practise accepting it without complaint. Most things fall into the second category. That is not bad news — it is the beginning of clarity."""),

    ("On Happiness", "Aristotle",
"""What is happiness? Aristotle thought most people had the question backwards.

They treated happiness as a feeling to be pursued — pleasure, comfort, the satisfaction of desire. Aristotle argued that happiness of this kind is not really happiness at all. It is what he called hedone — pleasure — and it is real and worth having, but it is not the point.

The Greek word he used for what he meant was eudaimonia, often translated as happiness but better understood as flourishing. Eudaimonia is not a feeling. It is a way of living. It is what happens when a human being is fully exercising their characteristic capacities — thinking well, acting well, engaging honestly with other people and with the world.

A knife is good when it cuts well. A doctor is good when they heal well. A human being flourishes when they are doing what human beings are distinctively capable of: exercising reason, developing virtue, living in genuine community with others.

This matters because it changes the question. Instead of asking 'how do I feel right now?' you ask 'am I becoming the person I am capable of becoming?' The first question can be answered by distraction. The second cannot.

Virtue, for Aristotle, was not an innate quality but a habit. Courage is developed by doing courageous things in the moments when it is difficult. Honesty is developed by telling the truth when a lie would be easier. Justice is developed by acting justly, repeatedly, until it becomes the natural expression of who you are.

He also insisted that flourishing is not a solo project. Humans are by nature social beings who need genuine friendship, real community, and participation in something larger than themselves. The good life, in Aristotle's account, is not comfortable. It is demanding, active, and shared. It requires you to become something, not merely to feel something."""),

    ("The Allegory of the Cave", "Plato",
"""Imagine prisoners chained in a cave since birth, facing a blank wall. Behind them, a fire burns. Between the fire and the prisoners, objects are carried back and forth, casting shadows on the wall ahead. The prisoners have never seen anything else. For them, the shadows are reality — they name them, study them, argue about them, and award prizes to the most skilled observer of shadows.

Now imagine one prisoner is unchained and turned toward the fire. The light is painful. The objects casting the shadows are confusing — they do not match what he thought he knew. Eventually he is dragged up and out of the cave, into the sunlight. At first he can see nothing. Gradually, he makes out reflections in water, then objects themselves, then the sun. He understands, now, what the shadows were.

Plato told this story to describe what education is and is not. Most people mistake education for the acquisition of information about the shadows — better techniques for categorising the familiar, more efficient ways of navigating what is already assumed to be real. Real education is the turning of the whole person. It is painful, disorienting, and it makes returning to the cave difficult.

The philosopher who returns to the cave — who tries to describe what they have seen outside — is not thanked. Their eyes have adjusted to the sunlight, and in the darkness they stumble. The other prisoners conclude that going up damages you.

What Plato was pointing at is the gap between appearance and reality, between the world as it is mediated to us and the world as it is. We are all, to some degree, watching shadows and calling them the whole truth.

The question the allegory asks is not abstract. It is personal: what are the walls of your particular cave? What are you not seeing because you have never been turned to face the light?"""),

    ("On Experience", "Michel de Montaigne",
"""Michel de Montaigne retired to his tower at thirty-eight, ostensibly to read and think. What he actually did was invent a new literary form — the essay — by doing something radical: he made himself the subject.

Not his opinions about great matters, but his actual experience of being alive. How he ate, what he feared, how his body changed, what he noticed when he was tired, what he thought about death when he thought about it honestly rather than performing courage. He called this 'essaying' — trying, testing, probing — and he turned it into a lifelong practice.

His central conviction was that experience is the best teacher, and most people avoid really paying attention to it. We read books about how to live. We study the lives of great men. We look outward for models and instructions. Meanwhile, the material that is most immediately available — our own thoughts, our own responses, our own patterns of behaviour — goes largely unexamined.

'Every man carries the form of the human condition within him,' Montaigne wrote. By examining himself honestly, he was not being narcissistic. He was doing something universal. The self is the most available laboratory for understanding what it is to be human.

What he found when he looked closely was not the consistent, rational, well-governed self he expected. He found contradictions, reversals, surprising weakness, and surprising resilience. He found that his judgments were unreliable, that certainty was usually a warning sign rather than an achievement.

He did not find this alarming. He found it interesting. And he concluded that wisdom was not the elimination of uncertainty but the ability to live well within it — to act, to commit, to engage, without pretending to a confidence you do not have.

The invitation in Montaigne's work is not to read him but to imitate him: to take your own experience seriously as a source of knowledge, to notice what you actually think rather than what you are supposed to think."""),

    ("On Distraction", "Blaise Pascal",
"""Blaise Pascal was a mathematical prodigy, a theologian, and one of the sharpest observers of human behaviour in the seventeenth century. His Pensees — fragments left at his death — contain one observation that has become almost unavoidably famous: 'All of humanity's problems stem from man's inability to sit quietly in a room alone.'

This is often quoted as a comment on restlessness. Pascal meant something more specific and more disturbing. He was describing what he called divertissement — diversion, distraction — and arguing that it is not a weakness but a strategy. People pursue distraction not because they are bored but because they are afraid.

Afraid of what? Of what appears when distraction is removed. Solitude, for most people, brings anxiety rather than peace, because it removes the noise that prevents us from thinking about things we would rather not think about. Our mortality. The gap between who we are and who we wish we were. The questions we have been too busy to answer, which turn out not to have gone anywhere.

'The sole cause of man's unhappiness,' Pascal wrote, 'is that he does not know how to stay quietly in his room.' He did not mean that people should become hermits. He meant that the ability to be alone with your own thoughts — without reaching immediately for a book, a conversation, a task — is rare and important, and that people who cannot do it are, in a specific sense, not free. They are governed by whatever provides the next distraction.

The mechanisms of distraction have multiplied enormously since the seventeenth century. The underlying impulse has not changed at all.

The question he leaves you with is not whether you are distracting yourself — almost everyone is — but what you are distracting yourself from. That is the thing worth sitting with, even briefly, even uncomfortably."""),

    ("On Deliberate Living", "Henry David Thoreau",
"""In the summer of 1845, Henry David Thoreau moved into a small cabin he had built himself on the shore of Walden Pond. He lived there for two years, two months, and two days. He went to explain himself afterward in a book that has been both celebrated and misunderstood ever since.

The most important sentence in Walden is probably this: 'I went to the woods because I wished to live deliberately, to front only the essential facts of life, and see if I could not learn what it had to teach, and not, when I came to die, discover that I had not lived.'

Deliberately. That is the word. Not successfully, not comfortably, not safely — deliberately. He wanted to know what he was actually doing with his days, and why, rather than continuing in the half-conscious drift he saw around him.

He was not recommending that everyone move to a pond. He was making a more portable point: that most people allow their lives to be shaped by forces they have never examined — convention, expectation, the need to appear respectable, the accumulation of things that require maintenance and gradually come to own their owners.

'The mass of men lead lives of quiet desperation,' he wrote. Not loud desperation — the drama of obvious crisis — but quiet desperation. The low-level sense that something has been missed, that the real thing has somehow been postponed indefinitely.

Thoreau's remedy was attention. Pay close attention to where your time actually goes, what your labour actually produces, what you genuinely need and what you have simply been told you need. Strip the unnecessary and see what is left.

The deeper invitation is not to read his conclusions — it is to run your own experiment, in whatever form that takes."""),

    ("On Self-Reliance", "Ralph Waldo Emerson",
"""'Trust thyself: every heart vibrates to that iron string.'

Emerson wrote Self-Reliance in 1841, and it remains one of the most demanding essays in the American tradition. Not demanding in the sense of difficult to read — Emerson's sentences are clear and forceful — but demanding in what it asks of the reader. It asks them to mean what they think.

His central argument is that each person contains an original relationship to the universe, an angle of perception that is genuinely their own. Most people, most of the time, abandon this in favour of conformity — agreeing with received opinion, following fashion, suppressing reactions that might seem strange, gradually editing themselves into an acceptable version that no one particularly needs.

Consistency, he argued, is usually a mask for cowardice. The man who ties himself to his past positions for fear of appearing inconsistent has substituted his reputation for his mind. 'A foolish consistency is the hobgoblin of little minds, adored by little statesmen and philosophers and divines. With consistency a great soul has simply nothing to do.'

This is not a licence for irresponsibility. Emerson was a deeply serious man. What he was attacking was the specific kind of consistency that refuses growth — the insistence on holding a position not because you have examined it recently but because you held it before, and changing it would require admitting you were wrong.

What he wanted instead was active, honest, ongoing engagement with your own experience and judgment. Not the judgment you are supposed to have, not the opinion that will make you liked, but what you actually think when you think carefully.

'To believe your own thought, to believe that what is true for you in your private heart is true for all men — that is genius.' It is also just good practice."""),

    ("On Becoming Who You Are", "Friedrich Nietzsche",
"""What Nietzsche spent much of his working life trying to articulate is the idea that becoming yourself is a task, not a given. Most people inherit their values, their tastes, their goals, their idea of what a good life looks like. They absorb them from family, culture, religion, and peer groups without examining them. They become a version of what the world expected, and call it an identity.

His phrase for the alternative was 'become what you are' — a paradox that rewards sitting with. You cannot become what you already are. The task is to discover what you might be if you stripped away the borrowed and the assumed, and then to actually build it through discipline, choice, and the willingness to fail in your own direction rather than succeed in someone else's.

He was not recommending selfishness or the rejection of all values. He was recommending honesty about where your values actually come from, and courage about replacing the ones that are not genuinely yours.

The aspect of Nietzsche that is most misunderstood is his hardness. He demanded a lot. He had little patience for comfort-seeking, for the use of philosophy as consolation rather than as a tool for honest self-examination. But the demand was not for suffering — it was for seriousness. He wanted people to take their own lives seriously enough to actually make something of them.

'What does your conscience say? You shall become who you are.' Not who you are told to be. Not who it is convenient to be. Not who is easiest to be in the company you currently keep.

The question is whether you are willing to find out, and then to do it."""),

    ("On Desire and Suffering", "Arthur Schopenhauer",
"""Arthur Schopenhauer believed that the fundamental nature of the universe is not reason, not goodness, not progress, but will — blind, striving, insatiable will. And he believed that humans, as expressions of this will, are trapped in a cycle of desire, temporary satisfaction, and renewed desire, with suffering as the default state.

His analysis of desire is precise: when we want something strongly, we suffer from the wanting. When we get it, we experience brief relief — not joy, but the temporary cessation of craving. Then a new desire fills the space, and the cycle begins again. 'Wealth is like sea-water; the more we drink, the thirstier we become.'

The person who has got everything they wanted is not satisfied — they are simply waiting for new discomfort to emerge. Boredom, which Schopenhauer took very seriously as a form of suffering, fills the gaps that unfulfilled desire would otherwise occupy.

This is not, however, the end of his philosophy. He thought the cycle could be interrupted in two ways. The first is aesthetic experience — art, music especially, which allows temporary escape from the will, a moment of pure contemplation without wanting. The second, more demanding, is the deliberate reduction of desire — not through repression but through clear-eyed recognition of its mechanics.

If you can see that the thing you want will not give you what you are expecting from it, the wanting changes texture. It does not disappear, but it loosens its grip. You can act from choice rather than compulsion.

Suffering is reduced not by getting more but by wanting less, not through acquisition but through the quieting of the will. This is not resignation — it is the beginning of something resembling peace."""),

    ("On Impermanence", "Marcus Aurelius",
"""'Loss is nothing else but change, and change is nature's delight.'

Marcus Aurelius returned to the theme of impermanence throughout the Meditations, not as a source of despair but as a practical tool for keeping perspective. Everything that exists, he noted, is in the process of becoming something else. The cities he governed, the emperors before him, the empires that had seemed permanent — all of them had dissolved or were dissolving. His own body, his thoughts, his memories — all temporary arrangements of matter that the universe would reclaim.

He did not say this to be dark. He said it because he found it clarifying.

When we forget that things are temporary, we relate to them badly. We grasp at pleasures as though keeping them is possible. We resist difficulties as though they should not exist. We treat our current situation — good or bad — as though it is the permanent state of affairs, which makes the good feel threatened and the bad feel endless.

Remembering impermanence does the opposite. It makes the good more vivid — you can appreciate something fully when you know it will not last forever. And it makes the bad more bearable — whatever this is, it is not permanent. The universe does not hold grudges.

He practised something he called the view from above — imagining his situation from a great height, as a brief moment in a very long story. From that height, the things that had seemed urgent and personal reduced in scale. Not to nothing — he took his responsibilities seriously — but to their actual size.

What matters to you? That is the question impermanence is designed to surface."""),

    ("On True Friendship", "Seneca",
"""'He who begins to be your friend because it is to his advantage to be so will also cease to be your friend when it is to his advantage to do so.'

Seneca was a careful student of friendship, partly because he had so much experience of its failure. Roman public life was saturated with instrumental relationships — alliances based on proximity to power, associations that lasted precisely as long as the mutual benefit did. He called these arrangements not friendship but convenience.

Real friendship required that you trusted the other person with your whole self — not the performed version, the socially acceptable face, but the actual person underneath, with their doubts and failures and unresolved questions. 'If you consider any man a friend whom you do not trust as you trust yourself, you have not understood what true friendship means.'

This level of trust is only possible between people who genuinely wish each other well — not for what they can provide, but in themselves. The test is simple: would the friendship survive the removal of any particular benefit? If one of you lost status, money, usefulness — would the other remain?

Seneca also wrote about the relationship between friendship and solitude. The person who cannot be alone cannot be a good friend, because they are using the friend to escape from themselves rather than genuinely engaging with them. And the person who has no friends — who is fully self-sufficient and asks nothing of others — is missing something essential to a full human life.

The ideal he described was a kind of midpoint: a self who can be alone comfortably, and who chooses friendship not out of need or habit but because genuine friendship multiplies what is best in both people."""),

    ("On Judgment", "Epictetus",
"""'Men are disturbed not by the things which happen, but by the opinions about the things.'

This is the core of Epictetus, and it is the kind of statement that sounds simple until you try to live by it.

The event itself — the insult, the setback, the loss — is not, in his view, what causes the suffering. What causes the suffering is the judgment you add to it: that this is terrible, that it should not have happened, that it says something definitive about you or the world. The event is a fact. The suffering comes from the story.

This is not a comfortable idea. It implies that a significant portion of your distress is, in some sense, self-generated — not the original events, but the elaboration you build around them. Most people resist this conclusion because it feels like it excuses whoever or whatever caused the original event. It does not. Epictetus was perfectly willing to call bad behaviour bad. The point is that your response to it, and the mental life you build around it, is still yours.

He recommended a practice of examining your judgments before they calcify. When you feel strongly about something — angry, afraid, resentful — pause. Ask what story you are telling yourself about the event. Then ask whether that story is the only possible story, and whether it is serving you.

This is not the same as positive thinking, which is merely substituting one uncritical story for another. It is examining the structure of your interpretation, finding where it is distorted by habit or fear, and correcting it.

The long-term goal Epictetus was describing was a kind of freedom that external circumstances cannot touch. A space between what happens and how you respond — a space you own and can use. Most people never develop it because they never notice it is there. It is always there."""),

    ("On Virtue as Habit", "Aristotle",
"""'We are what we repeatedly do. Excellence, then, is not an act but a habit.'

The phrasing is modern, but the idea is accurately Aristotle's. The Nicomachean Ethics — his extended investigation into how to live well — returns again and again to a single crucial insight: character is not something you have, it is something you build through repeated action.

This runs counter to a common assumption, which is that character is essentially fixed. Either you are an honest person or you are not; either you are courageous or you are not. Aristotle disagreed. He thought virtues were skills, and that they developed the way all skills develop — through practice, failure, correction, and more practice.

The brave person became brave by doing brave things, repeatedly, especially when it was uncomfortable. The just person became just by acting justly in situations where injustice would have been easier. The first iterations were imperfect and required conscious effort. Over time, through repetition, the behaviour became natural — an expression of character rather than a deliberate act.

This means that virtue is always either growing or diminishing. It is not a status you achieve and keep. Every day that you act in accordance with your values reinforces them; every compromise makes the next compromise easier.

He introduced the concept of the mean — the idea that most virtues sit between two vices. Courage is between cowardice and recklessness. Generosity is between stinginess and profligacy. The skill is not hitting an abstract target but developing the sensitivity to recognise what the situation requires.

What Aristotle's account demands, practically, is that you take your small daily actions seriously. The person you are becoming is the sum of the person you are choosing to be, repeatedly, in ordinary moments."""),

    ("On the Examined Life", "Plato",
"""'The unexamined life is not worth living.'

Socrates said this at his trial, in 399 BC, when he was being offered a choice between exile and death. He chose death — not because he was reckless, but because exile would have required him to stop doing the one thing he believed was genuinely valuable: questioning.

Plato's dialogues are mostly Socrates in conversation, pursuing a question through a series of exchanges that typically reveal how much less clear the initial position was than the speaker thought. The experience of being in dialogue with Socrates was deeply unsettling. You entered the conversation confident you understood courage, or justice, or piety. You left aware that you did not, and with something harder: the genuine question in place of the comfortable assumption.

This was not a popular service. Most people, Socrates observed, prefer the comfortable assumption. They know what courage is — it is fighting well — and they would rather keep that simple definition than engage with the complications that emerge if you press it.

The Socratic method is sometimes taught as a debating technique. It is more like a hygiene practice. Its purpose is not to win arguments but to clear out the false certainties that accumulate in the mind — the positions held by habit or social pressure rather than genuine thought, the ideas that have never been tested because testing them would be uncomfortable.

Examining your life does not mean being paralysed by self-criticism or unable to act without philosophical certainty. It means being willing to ask, occasionally and honestly, why you hold the beliefs you hold, why you want the things you want, and whether your actions are actually consistent with the values you claim.

Most people find, when they do this seriously, that there is a gap. The question is what to do with it."""),

    ("On Solitude", "Michel de Montaigne",
"""'We should reserve a back shop all our own, entirely free, in which to establish our real liberty and our principal retreat and solitude.'

Montaigne wrote this in his essay on solitude, and the image of the back shop is one of the most useful metaphors in his work. Not a hermitage, not a permanent withdrawal from the world — just a room behind the room, a part of yourself that belongs to no one, that is not for sale or loan, that remains yours regardless of what is happening at the front of the shop.

He had been a magistrate, a mayor, a diplomat. He knew something about the way public life colonises the self — the way the roles we perform, the expectations we meet, the personas we maintain gradually take up all the available space, leaving less and less room for whatever the actual person underneath might think or feel.

The back shop is a remedy for this. It is not about rejecting responsibility or fleeing difficulty. It is about maintaining a private interior that does not depend on external circumstances for its stability. When everything outside is turbulent — and in Montaigne's life, which spanned the French religious wars, it frequently was — the person with a functioning interior can absorb the disruption without being destroyed by it.

He was also making an argument against the kind of retirement that merely relocates the same anxieties to a different setting. A person who moves to the country still carries their restlessness with them; a person who withdraws from social life without developing an inner life finds that solitude is not peaceful but amplified.

Real solitude, in Montaigne's sense, requires that you can be interesting to yourself — that you have genuine inner resources, a relationship with your own experience that does not depend on external stimulation to sustain it. This is cultivated, over time, by the habit of attention."""),

    ("On Foolish Consistency", "Ralph Waldo Emerson",
"""There is a kind of cowardice that is very hard to see because it looks like virtue. Emerson called it conformity, and spent much of Self-Reliance anatomising exactly how it works.

You have a thought — genuine, original, your own. Then you consider your audience. You consider what they are likely to think, whether it will make you seem odd, whether it will cause conflict. You soften the thought, or you keep it private, or you simply do not have it again. Over time, this becomes habitual. The original thoughts stop forming, and the public version of you becomes more and more thoroughly other people's creation.

Emerson's remedy was blunt: speak your thought. Not recklessly, not without consideration, but without the editing that is really just fear. 'Whoso would be a man, must be a nonconformist.' Not contrarian — Emerson was not recommending disagreement for its own sake — but genuinely, even inconveniently, oneself.

The specific consistency he attacked was the kind that protects past positions not because they are right but because changing them requires admitting error. 'A foolish consistency is the hobgoblin of little minds.' The mind that has actually been working, that has encountered new evidence, that has taken new experience seriously, will change its positions. That is not weakness — it is the sign of a functioning intellect.

What he wanted instead was internal consistency — fidelity to your own best thinking rather than to the accumulated record of your past thinking. These are very different things. The first requires courage in the present; the second only requires memory.

The test he offers is uncomfortable: say the thing you actually think in the next conversation where it becomes relevant, without softening it to match the expected reaction. For most people, what remains is less than they assumed."""),

    ("On Retirement and Retreat", "Seneca",
"""Late in his life, Seneca began withdrawing from public life — carefully, gradually, in ways that would not provoke the suspicion of an emperor who had reason to be suspicious of him. In his letters to Lucilius, he reflects on what withdrawal is and is not for, and the reflection is still useful.

He was clear that physical retreat is not the same as inner retreat. The person who retires to a villa in the countryside while carrying their ambitions, resentments, and restlessness with them has not retreated at all. They have simply relocated. A crowd, he noted, can be a crowd of one — your own unexamined thoughts, circling.

What genuine retreat offers is the opportunity to stop performing. In public life, even private life in most households, there is always an audience, always a role being played, always some version of yourself being maintained for the sake of others. Solitude removes this. What remains is what you actually are, which can be either illuminating or alarming, depending on how long you have been avoiding it.

Seneca recommended a practice of regular, brief retreats — not extended withdrawals, but daily periods of quiet, of stepping back from the demands and the stimulation, of asking what you think rather than what you are expected to think. Not long. An hour, perhaps. But uninterrupted.

The goal was not peace, exactly — though peace is part of it. The goal was accuracy. When you have been in company for a long time, your sense of yourself is partly a reflection of how others see you. Regular solitude corrects for this. You remember what you actually value, what you actually think, what is going on beneath the social surface.

'Retire into yourself as much as you can.' Not as an escape from responsibility, but as the thing that makes genuine responsibility possible."""),

    ("On Small Actions", "Marcus Aurelius",
"""The Meditations contain almost no dramatic advice. There are no instructions for conquering fear, no methods for achieving greatness, no frameworks for becoming extraordinary. What they contain, almost entirely, is guidance about small things: how to begin a day, how to think about difficult people, what to do with irritation, how to handle the gap between what you intended and what you managed.

This is not a limitation of the book. It is the point.

Aurelius governed an empire and still understood that the quality of a life is made of small moments, most of them unremarkable. The decision whether to be patient with a tiresome person. The choice to do the necessary work rather than the enjoyable work. The private response to news you would prefer to be different. None of these feel significant. Together they are everything.

He returned again and again to a simple structure: this is what I believe, this is where I failed to act on it, this is what I will try to do differently. Not flagellation, not perfectionism — just honest accounting, and adjustment.

He wrote about the retreat into yourself — not as a withdrawal from action but as the practice of returning to your values before engaging. When you are about to respond to someone, or make a decision, or take an action that matters: pause briefly. Ask what you actually believe is right here, not what is expedient or easy or expected. Then do that.

The gap between knowing what is right and doing what is right is not usually a gap in knowledge. It is a gap in the moment — the half-second between the stimulus and the response where habit and character actually live. Aurelius was trying to widen that gap, through writing, through practice, through the daily discipline of returning to the same questions.

'Confine yourself to the present.' Not because the future does not matter, but because the present is where you actually are, and it is only here that anything can be done."""),
]

# ── Weight logic ──────────────────────────────────────────────────────────────
def current_weight(q):
    last = q.get("last_sent")
    if not last:
        return 1.0
    weeks = (date.today() - datetime.fromisoformat(last).date()).days // 7
    return min(1.0, weeks / DECAY_WEEKS)

# ── Load quotes ───────────────────────────────────────────────────────────────
try:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        quotes = json.load(f)
except FileNotFoundError:
    raise SystemExit(f"Error: {JSON_FILE} not found.")

for q in quotes:
    q.setdefault("weight", 1.0)
    q.setdefault("last_sent", None)

weights = [current_weight(q) for q in quotes]
chosen_quotes = random.choices(quotes, weights=weights, k=NUM_QUOTES)

# ── Fetch RSS news ────────────────────────────────────────────────────────────
def fetch_rss(feeds, n=3):
    items = []
    for url in feeds:
        if len(items) >= n:
            break
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=8) as r:
                root = ET.fromstring(r.read())
            ns = {"atom": "http://www.w3.org/2005/Atom"}
            # RSS 2.0
            for entry in root.iter("item"):
                title = (entry.findtext("title") or "").strip()
                link  = (entry.findtext("link")  or "").strip()
                if title and link:
                    items.append((title, link))
                if len(items) >= n:
                    break
            # Atom
            if len(items) < n:
                for entry in root.findall(".//atom:entry", ns):
                    title = (entry.findtext("atom:title", namespaces=ns) or "").strip()
                    link_el = entry.find("atom:link", ns)
                    link = (link_el.get("href", "") if link_el is not None else "").strip()
                    if title and link:
                        items.append((title, link))
                    if len(items) >= n:
                        break
        except Exception:
            continue
    return items[:n]

finance_news = fetch_rss(FINANCE_FEEDS, 3)
tech_news    = fetch_rss(TECH_FEEDS,    3)

# ── Chess lessons (rotated daily) ────────────────────────────────────────────
CHESS_LESSONS = [
    ("Control the Centre",        "Your first priority in any game. Place pawns on e4/d4 (or e5/d5 as Black) and develop pieces toward the middle. A piece in the centre controls more squares than one on the edge."),
    ("Develop Every Piece",       "Get your knights and bishops off the back rank before you start attacking. A rule of thumb: don't move the same piece twice in the opening unless you have to. Every undeveloped piece is a wasted turn."),
    ("King Safety — Castle Early","After developing your minor pieces, castle. Your king is a liability in the centre during the middlegame. Castling tucks it away and connects your rooks."),
    ("The Fork",                  "A fork is a single piece attacking two enemy pieces at once, forcing your opponent to lose one. Knights are the best forkers — their L-shape lets them attack squares no other piece covers. Always scan for knight forks after exchanges."),
    ("The Pin",                   "A pin locks a piece in place because moving it would expose a more valuable piece behind it. Absolute pins (pinned to the king) are the strongest — the piece literally cannot move. Use pins to win material or restrict your opponent."),
    ("The Skewer",                "The reverse of a pin. You attack a high-value piece; when it moves, you win the lesser piece behind it. Rooks and bishops are the classic skewering pieces. Look for skewers along open files and diagonals."),
    ("Discovered Attack",         "Move one piece to unleash an attack from another behind it. The moving piece can also create its own threat, making it doubly dangerous. Discovered checks are especially powerful — your opponent must deal with the check first."),
    ("Rooks Belong on Open Files","A rook on a closed file does almost nothing. Put rooks on files with no pawns, or half-open files (no friendly pawn). Two rooks doubled on an open file is one of the most powerful structures in chess."),
    ("Trade Pieces When Ahead",   "If you're up material, simplify. Trade pieces to reduce your opponent's counterplay and make your advantage easier to convert. Avoid trades when you're behind — you need chaos and complications to come back."),
    ("The 1-2-3 of Pawn Endings", "In king-and-pawn endgames, three things win: (1) King activity — centralise your king immediately. (2) Passed pawns — a pawn with no opposing pawn blocking it or on adjacent files. (3) Opposition — the side whose king forces the other back. Learn these and you'll convert endgames others draw."),
    ("Don't Move Your Queen Early","A premature queen sortie gets punished. Your opponent develops with tempo by chasing it. Bring out knights and bishops first, secure your king, then activate the queen when it has safe, useful squares."),
    ("Think in Forcing Moves First","Before any move, scan for checks, captures, and threats — in that order. Forcing moves limit your opponent's options. Calculate those lines before quieter moves. Many games are decided by a tactic hiding in plain sight."),
    ("Pawn Structure is Permanent","Unlike pieces, pawns can't go backwards. Doubled pawns, isolated pawns, and backward pawns are long-term weaknesses. Before pushing a pawn, ask: what does this create? Weak squares and open files last the whole game."),
    ("The Outpost",               "A square that can't be attacked by an enemy pawn is an outpost. A knight planted on an outpost deep in enemy territory is often worth as much as a rook. Create outposts by trading or advancing pawns to clear the attacking pawn."),
    ("Rook + King Checkmate",     "The most common endgame to know. Use the ladder method: put your rook on the edge of the board, drive the enemy king to the edge rank by rank, then bring your king over to help deliver mate. Practice this until it's automatic."),
    ("Bishops vs Knights",        "Open positions favour bishops — they cover long diagonals and distant squares quickly. Closed positions with locked pawns favour knights — they can hop over pawns and reach squares bishops can't. Always consider which piece suits the structure."),
    ("The Zwischenzug",           "A 'between move' — instead of recapturing immediately, you play a forcing move first (usually a check or big threat). Your opponent must respond, and then you recapture, often with an improved result. Always ask: before I take back, is there something better?"),
    ("Piece Activity Over Material","A rook doing nothing is worth less than a bishop tearing up a diagonal. When evaluating a position, ask how active each piece is. Sometimes sacrificing a pawn to open lines and activate your pieces is objectively stronger than holding the material."),
    ("Triangulation",             "A king manoeuvre in endgames to lose a tempo and gain the opposition. If your king needs to reach a square but direct paths keep the opposition equal, triangulate — take three moves to do what one would, forcing your opponent into a losing structure."),
    ("The 50-Move Rule & Zugzwang","In endgames, two concepts matter: zugzwang (any move you make worsens your position — used to force a win) and the 50-move rule (50 moves without a capture or pawn move = draw). Knowing these prevents you from winning a won endgame incorrectly or letting a draw slip."),
]

# ── Pick today's reading & chess lesson ──────────────────────────────────────
passage_title, passage_author, passage_text = PASSAGES[date.today().toordinal() % len(PASSAGES)]
passage_html = passage_text.strip().replace('\n\n', '<br><br>')
chess_title, chess_body = CHESS_LESSONS[date.today().toordinal() % len(CHESS_LESSONS)]

# ── Build HTML email ──────────────────────────────────────────────────────────
def news_rows(items, fallback_label):
    if not items:
        return f"<tr><td style='padding:6px 0;color:#888;'>Could not fetch {fallback_label} news.</td></tr>"
    rows = ""
    for title, link in items:
        rows += (
            f"<tr><td style='padding:5px 0;'>"
            f"<a href='{link}' style='color:#1a73e8;text-decoration:none;'>{title}</a>"
            f"</td></tr>"
        )
    return rows

html_body = f"""
<!DOCTYPE html>
<html>
<body style="font-family:Georgia,serif;max-width:620px;margin:0 auto;padding:24px;color:#222;">

  <!-- Quote -->
  <h2 style="font-size:16px;font-weight:normal;color:#555;margin-bottom:24px;">
    Today's thought
  </h2>
  {"".join(f'<blockquote style="border-left:3px solid #ccc;margin:0 0 16px 0;padding:8px 16px;font-style:italic;color:#333;">{q["quote"]}</blockquote>' for q in chosen_quotes)}

  <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">

  <!-- Finance -->
  <h3 style="font-size:14px;letter-spacing:.05em;text-transform:uppercase;color:#888;margin:0 0 10px 0;">
    Finance
  </h3>
  <table style="width:100%;border-collapse:collapse;">
    {news_rows(finance_news, "finance")}
  </table>

  <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">

  <!-- Tech -->
  <h3 style="font-size:14px;letter-spacing:.05em;text-transform:uppercase;color:#888;margin:0 0 10px 0;">
    Technology
  </h3>
  <table style="width:100%;border-collapse:collapse;">
    {news_rows(tech_news, "tech")}
  </table>

  <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">

  <!-- Chess -->
  <h3 style="font-size:14px;letter-spacing:.05em;text-transform:uppercase;color:#888;margin:0 0 10px 0;">
    Chess
  </h3>
  <p style="margin:0 0 6px 0;font-size:14px;font-weight:bold;color:#333;">{chess_title}</p>
  <p style="margin:0;font-size:14px;color:#444;line-height:1.6;">{chess_body}</p>

  <hr style="border:none;border-top:1px solid #eee;margin:24px 0;">

  <!-- Reading -->
  <h3 style="font-size:14px;letter-spacing:.05em;text-transform:uppercase;color:#888;margin:0 0 10px 0;">
    Reading
  </h3>
  <p style="margin:0 0 4px 0;font-size:15px;font-weight:bold;color:#333;">{passage_title}</p>
  <p style="margin:0 0 14px 0;font-size:13px;color:#999;font-style:italic;">— {passage_author}</p>
  <p style="margin:0;font-size:14px;color:#444;line-height:1.75;">{passage_html}</p>

</body>
</html>
"""

# ── Send email ────────────────────────────────────────────────────────────────
def send_email():
    if not (EMAIL_ADDRESS and EMAIL_PASSWORD and EMAIL_RECEIVER):
        raise SystemExit("Error: Missing e-mail credentials in environment.")

    msg = MIMEMultipart("alternative")
    msg["From"]    = EMAIL_ADDRESS
    msg["To"]      = EMAIL_RECEIVER
    msg["Subject"] = "Today's thought"
    msg.attach(MIMEText(html_body, "html"))

    try:
        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.sendmail(EMAIL_ADDRESS, EMAIL_RECEIVER, msg.as_string())
        server.quit()
        print("Email sent successfully.")
    except Exception as e:
        print("SMTP error:", e)

# ── Update weights & save ─────────────────────────────────────────────────────
def mark_as_sent():
    today_str = date.today().isoformat()
    for q in chosen_quotes:
        q["weight"]    = 0.0
        q["last_sent"] = today_str
    with open(JSON_FILE, "w", encoding="utf-8") as f:
        json.dump(quotes, f, ensure_ascii=False, indent=2)

# ── Execute ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    send_email()
    mark_as_sent()
