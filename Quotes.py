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
    "https://feeds.apnews.com/rss/apf-business",
    "https://feeds.npr.org/1006/rss.xml",
    "https://feeds.reuters.com/reuters/businessNews",
]

TECH_FEEDS = [
    "https://phys.org/rss-feed/",
    "https://www.sciencedaily.com/rss/top/technology.xml",
    "https://feeds.arstechnica.com/arstechnica/science/",
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

    ("The Absurd", "Albert Camus",
"""There is only one truly serious philosophical question, and that is suicide. Whether life is worth living — this is where Camus began, and the answer he arrived at was both defiant and joyful.

His starting point was what he called the absurd: the collision between the human need for meaning and the universe's complete indifference to that need. We are creatures who demand that things make sense, that suffering have a purpose, that effort be rewarded. The universe offers none of this. It is silent, indifferent, and does not negotiate.

Most people deal with this by what Camus called philosophical suicide — leaping into a belief system that explains away the collision. Religion, ideology, optimism about progress. These are all, in his view, evasions. They refuse the absurd rather than confronting it.

His alternative was to live with it. To acknowledge fully that life offers no ultimate meaning, and then to live as richly and deliberately as possible anyway. Not in despair — despair would require the belief that meaning should exist and does not. But in revolt: a clear-eyed, defiant insistence on living fully despite the silence.

He found his image for this in Sisyphus, condemned by the gods to roll a boulder up a hill forever, only to watch it roll back down. The myth is usually read as a picture of futile suffering. Camus read it differently. Sisyphus, descending the hill to begin again, is aware of his situation. He has no illusions. And in that awareness, Camus argued, lies a kind of freedom. His struggle is his own. His effort is real.

'One must imagine Sisyphus happy.' This is not irony. It is the most demanding thing Camus ever said."""),

    ("On Bad Faith", "Jean-Paul Sartre",
"""Sartre's most uncomfortable idea was not that God does not exist. It was that the consequences of that absence fall entirely on us.

If there is no God, there is no fixed human nature — no essence that precedes our existence and tells us what we should be. We arrive in the world first, and we define ourselves through what we choose. 'Existence precedes essence.' This sounds liberating. The weight of it, Sartre insisted, is enormous.

Because if we define ourselves through our choices, we cannot blame our nature, our upbringing, or our circumstances for what we are. We are, at every moment, what we have chosen to be. And we are, at every moment, choosing.

Bad faith is the strategy of pretending otherwise. The waiter who plays at being a waiter so completely that he forgets he chose the role. The man who says 'I have a violent temper' as though violence were a geological feature rather than a repeated choice. The woman who refuses a decision by allowing circumstances to decide, then pretends she had no choice.

These are all ways of fleeing freedom — of pretending to be a thing rather than a person, a product of forces rather than a source of them.

Sartre did not think bad faith was easily escaped. The temptation to be something solid and defined, rather than the anxious openness of genuine freedom, is very strong. But he thought the honest response to the human condition was to face it — to acknowledge that you are always choosing, always responsible, always the author of what you are becoming."""),

    ("On Anxiety and Freedom", "Søren Kierkegaard",
"""Anxiety, for Kierkegaard, is not a disease to be cured. It is the feeling that accompanies freedom, and it is inseparable from being genuinely human.

He described it as the dizziness of freedom — the vertiginous sensation at the edge of possibility. When you stand before a genuine choice, one that actually matters, you feel it: the awareness that you could go one way or the other, that neither way is guaranteed, that you must choose and then live with what you chose. That feeling is anxiety, and it is not pathological. It is what freedom feels like from the inside.

Most people spend their lives avoiding this feeling. They fill every hour, commit to every existing obligation, follow convention so closely that genuine choice never appears. They are, in his terms, living on the surface of experience — moving from sensation to sensation, never arriving anywhere that requires them to be someone.

The move he called for was inward — a willingness to face your own anxiety rather than escape it, to acknowledge that you are a self that must be built rather than a role that can be played. This is what he meant by the leap: not blind faith, but the willingness to commit, to choose, to take responsibility for a direction when no certainty is available.

The alternative — living entirely within convention, following the crowd, never choosing in any deep sense — he called the despair of not being oneself. It is the most common form of despair, he thought, precisely because it does not feel like despair. It feels like security.

What Kierkegaard wanted people to feel was the weight of their own existence. Not to crush them, but to wake them up."""),

    ("On Learning and Character", "Confucius",
"""Confucius spent most of his life failing, by conventional measures. He held official positions, lost them, wandered from state to state offering counsel to rulers who mostly ignored him, and died without seeing his ideas implemented. His success was posthumous, and vast.

What he was trying to build, in the small community of students who did follow him, was a specific kind of person: the junzi — the superior man. Not superior by birth or position, but by character — by the quality of attention, care, and effort brought to every relationship and every responsibility.

The core of his teaching was that character is formed through practice, and practice begins with attention. Pay attention to how you treat the people immediately around you. The quality of your relationships with your family is the foundation of the quality of your relationships with everything else. Get that right first.

He was suspicious of people who could speak movingly about virtue without embodying it in ordinary conduct. 'Fine words and an insinuating appearance are seldom associated with true virtue.' The test was not what you said but what you did — not in large, visible moments, but in the daily texture of how you treated people who had nothing to give you.

Learning, for Confucius, was not the accumulation of information. It was the progressive refinement of perception and response — becoming someone who could see what each situation actually required and who had built the habits to respond appropriately. This required constant reflection: examining yourself daily on whether you had been faithful in your dealings, sincere with your friends, and diligent in what you had been taught.

The examination was the practice."""),

    ("On the Way", "Laozi",
"""The Tao Te Ching is eighty-one short chapters, and most of them concern the same thing: the difference between forcing and allowing.

Laozi's central insight is that the world has its own nature, its own tendency, its own way of unfolding. When you work with that nature rather than against it, everything becomes possible and effort becomes effortless. When you work against it — insisting that things be other than they are, forcing outcomes that the situation is not ready to produce — you generate resistance, friction, and eventual exhaustion.

He called this principle wu wei — often translated as non-action, but better understood as non-forcing. Not passivity, but action that is in harmony with circumstances rather than in opposition to them. The most skilled craftsman does not fight his material; he understands it so well that working with it looks easy.

Water is his recurring image. Water is the softest thing in the world, and it wears away rock. It does not fight the rock — it simply keeps moving, and it finds every available path. It always goes lower, seeking the humble place, and nothing can stop it in the long run.

The practical implication is a suspicion of urgency, of striving, of the insistence on controlling outcomes. Not because outcomes do not matter, but because desperate grasping often produces the opposite of what is wanted. The plant grows better when you stop pulling it upward.

'Do you have the patience to wait until the mud settles and the water is clear?' That is not a passive question. It is one of the most demanding questions in philosophy."""),

    ("On Suffering and Liberation", "The Buddha",
"""The first teaching the Buddha gave after his enlightenment was the most compressed and most demanding: life involves suffering; suffering has a cause; the cause can be ended; there is a path that ends it.

He was not being pessimistic. He was being precise. The word he used, dukkha, covers more than suffering — dissatisfaction, the sense that things are slightly off, the low-level discomfort of impermanence that runs beneath even pleasant experience. The observation was not that life is terrible but that it is fundamentally unsettled, and that we spend enormous energy pretending otherwise.

The cause he identified was craving — thirst. Not just the obvious desires for things we want and do not have, but the subtler grasping at experiences, the clinging to what is pleasant, the aversion to what is unpleasant. The self that is doing the grasping is itself part of the problem — it is not a fixed thing that has desires; it is, in part, constituted by them.

This does not mean the goal is extinction or joylessness. The path he described covers right understanding, right intention, right speech, right action, right livelihood, right effort, right mindfulness, right concentration. These are not rules imposed from outside but descriptions of how a person who has seen clearly tends to live.

What liberation looks like from inside, he was reluctant to describe — not because it is unknowable but because any description risks becoming another object to grasp at. The direction, though, is clear: toward less clinging, less reactivity, more presence, more compassion. Not away from the world, but more fully in it."""),

    ("On Meaning", "Viktor Frankl",
"""Viktor Frankl survived Auschwitz, Dachau, and two other concentration camps. He was a psychiatrist before the war and became one after it. What he discovered was the basis for logotherapy — the idea that the search for meaning is the primary motivation in human life.

He watched men die in the camps, and he watched men survive conditions that should have killed them. The difference, he came to believe, was not physical strength alone. It was whether a person had something to live for — a future self they could imagine, a task they felt called to complete, a person they needed to return to. Those who could locate meaning had a resource the others did not.

'He who has a why to live can bear almost any how.' He quoted Nietzsche, and he meant it literally. The suffering did not diminish; the conditions did not improve. What changed was the relationship to the suffering. When it had a context — when it could be seen as a test, a sacrifice, a means to some future end — it could be endured. When it was simply pointless, it destroyed people.

His conclusion was both urgent and practical: do not wait for meaning to present itself. Ask what life is demanding of you. The question is not what you expect from life but what life expects from you, in this situation, right now. The answer may be very small — to comfort someone nearby, to do this piece of work with care, to simply endure with dignity. It does not need to be large to be real.

He also insisted that meaning is found, not manufactured. You cannot decide that something is meaningful and make it so by force of will. You discover it by paying honest attention to what actually calls to you."""),

    ("On Idle Curiosity", "Bertrand Russell",
"""Russell argued against a culture that had made busyness a moral virtue. The man who never stops working is admired; the man who spends an afternoon following an idea wherever it leads, reading something with no practical application, simply thinking — he is suspected of laziness. Russell thought this exactly backwards.

The things that have most changed human life, he argued, have rarely come from people working efficiently toward known ends. They have come from people pursuing curiosity without a predetermined destination. The history of science is largely the history of inquiries that seemed useless at the time. Pure mathematics, pursued for centuries with no practical goal, turned out to underlie all of modern physics.

But his deeper point was not about scientific progress. It was about what kind of person the capacity for idle curiosity makes you. The person who can be genuinely interested in something that does not concern their immediate situation has a wider relationship with the world. They are less trapped in their own preoccupations. They are better company. They are less likely to be fooled by simple answers, because they have spent time with complex ones.

He thought the goal of education was not to produce people who could perform useful tasks, but people who had genuine interests — who were pulled toward ideas and questions for their own sake, and who had the capacity to follow that pull without needing it to pay off immediately.

'The good life is one inspired by love and guided by knowledge.' The knowledge he had in mind was not credentials or information. It was the kind of understanding that comes from sustained, disinterested attention — the attention that curiosity makes possible."""),

    ("On Moral Duty", "Immanuel Kant",
"""Kant thought that most ethical thinking was confused because it started in the wrong place. Consequentialists ask about outcomes. Virtue ethicists ask about character. Kant thought both were asking the wrong question. The right question was: what can I will as a universal law?

His categorical imperative is actually very practical. When you are tempted to lie because it is convenient, to break a promise because keeping it is difficult, ask: what if everyone did this? Not just occasionally, but as a universal principle? If the practice becomes self-defeating or unjust at universal scale, you should not do it. The principle is not about consequences — it is about consistency.

He also insisted on something simpler and more demanding: treat people always as ends in themselves, never merely as means. This is not an instruction to be nice. It is an instruction to recognise the full humanity of every person you deal with — their capacity for reason, their own projects and purposes, their right to make their own decisions. To use someone purely for your own ends, without regard for their interests or consent, is to treat them as a tool rather than a person.

What makes Kantian ethics difficult is that it allows no exceptions. The duty to tell the truth, in his account, holds even when lying would produce better outcomes. Most people cannot accept this, and many philosophers agree. But the rigour is the point — Kant was trying to describe what morality actually demands, not what is convenient.

'Act only according to that maxim by which you can at the same time will that it should become a universal law.' Simple to state. Very difficult to live by."""),

    ("On Reason and Passion", "David Hume",
"""Hume made a claim so radical that it still provokes: reason is, and ought only to be, the slave of the passions.

He meant this precisely. Reason, by itself, can only tell us what is true — what the world is like, what causes what, what consequences follow from what actions. It cannot, by itself, tell us what to want or what to do. For that, you need desire, feeling, care. Reason without passion has no direction. It can compute the most efficient route to any destination but cannot choose the destination.

This sounds like an argument for being driven by emotion. Hume did not mean that. He thought the emotions that typically drove people — vanity, fear, greed, short-term pleasure-seeking — were often unreliable guides. What he was saying was that even the most careful, rational person is ultimately moved by caring about something. The philosopher who values truth is still valuing something; reason did not produce that valuing.

He was also one of the first philosophers to take seriously the question of moral psychology — not just what we should value, but why we value what we value, how sympathy works, how we come to care about people beyond our immediate circle. His answer was that sympathy — the capacity to imaginatively inhabit another's perspective — is the foundation of moral concern.

The implication he drew was modest and important: rather than pretending our ethical reasoning is purely rational, we should understand its emotional roots — and try to cultivate the right emotions, the ones that lead to genuine concern for others rather than mere concern for appearance."""),

    ("On Method and Doubt", "René Descartes",
"""Descartes decided, at some point in his thirties, to doubt everything he had ever been told. Not as a permanent state, but as a method. He wanted to find something he could know with absolute certainty, and the only way to find it was to strip away everything that could possibly be doubted.

What can you doubt? The evidence of your senses — they deceive you regularly. The external world — perhaps everything you perceive is a dream. Mathematics — even simple arithmetic might be the product of a deceiving demon arranging your mind. He doubted everything he could doubt, methodically, and found one thing he could not doubt: that he was doubting. The very act of doubting presupposed a doubter. 'I think, therefore I am.'

This is not just a clever argument. It established the thinking subject as the foundation of knowledge — consciousness, mind, the inner life — as the one thing that could not be dissolved by sceptical doubt. Everything else had to be rebuilt on this basis.

The method itself is perhaps more useful than the specific result. When you want to know what you actually believe versus what you have simply absorbed, the Cartesian move is to ask: can I doubt this? What would it take to show this false? What remains when I strip away the claims I cannot verify?

Most people never run this procedure on their most important beliefs. They have inherited positions on politics, morality, religion, and human nature from their culture and upbringing, and have never examined them. Descartes thought systematic doubt was the beginning of intellectual honesty, and he was right."""),

    ("On Freedom and Necessity", "Baruch Spinoza",
"""Spinoza's Ethics is one of the most unusual books in Western philosophy: written in the form of a geometry textbook, with definitions, axioms, propositions, and proofs. The subject is how to be free.

His argument begins with determinism. Everything that happens, happens necessarily — according to the laws of nature. Human beings are no exception. Your thoughts, your desires, your choices — all follow necessarily from prior causes. In one sense, you have no free will.

But Spinoza thought this conclusion was liberating rather than defeating, because he had a different idea of what freedom means. Freedom is not the absence of causation — nothing is free from causation. Freedom is acting from your own nature rather than from external compulsion. A free action is one that flows from your own understanding rather than from passion or ignorance.

Passion, in his account, is what happens when you are moved by causes you do not understand — when you are angry without knowing why, fearful of things that are not actually threatening, driven by desires you cannot explain. The remedy is not to suppress these passions but to understand them. When you truly understand why you feel what you feel, the feeling changes character. It loses its compulsive quality.

The highest good, for Spinoza, was what he called the intellectual love of God — the contemplative understanding of the whole, of which you are a part. This is not a religious sentiment but a philosophical one: the peace that comes from understanding your place in the necessary unfolding of things, and accepting it without either resistance or resentment."""),

    ("On Anger", "Marcus Aurelius",
"""Of all the subjects Marcus Aurelius returns to in the Meditations, anger gets the most attention. He was an emperor surrounded constantly by incompetence, ingratitude, and bad faith. He was also committed, by philosophy and temperament, to not being controlled by any of it.

His analysis of anger is precise. When someone wrongs you or behaves badly, you have two choices: you can be angry, or you can be useful. Anger does not repair the wrong. It does not improve the person who behaved badly. It does not make you more capable of responding well. It consumes your attention, distorts your judgment, and leaves you exhausted. The only person it reliably harms is you.

He did not mean that wrongs should be ignored or injustice passively accepted. He was an active ruler who made decisions about justice daily. The point was about the internal state in which those decisions are made. You can act firmly, clearly, even forcefully, without being driven by anger. In fact, you act better without it — more clearly, with better judgment about what the situation actually requires.

He returned again and again to the people who most provoked him, and asked himself to understand them. Not to excuse them, but to understand them. 'When you wake up in the morning, tell yourself: the people I deal with today will be meddling, ungrateful, arrogant, dishonest, jealous and surly.' Not as a counsel of despair, but as a preparation. You will encounter these people. You will be less surprised and more useful if you have anticipated them.

The goal was not serenity for its own sake but clarity in action."""),

    ("On Anger", "Seneca",
"""Seneca wrote an entire book on anger — De Ira — and it is probably the most practically useful thing he produced. His opening observation is blunt: no passion is more eager for revenge, more capable of violence, and more terrible in its effects; yet none more shameful in its cause.

He was interested in what anger actually is. It begins with an injury — real or imagined — followed immediately by an evaluation: this was unjust, this was deliberate, this deserves a response. The anger is not the injury; it is the interpretation applied to the injury. And interpretations can be examined.

Most of what makes people angry, he observed, is not actually as bad as it feels in the moment. The delay that seemed deliberate was an accident. The slight that seemed intentional was carelessness. The refusal that felt like contempt was simply someone else's limitation. None of this means the anger was wrong to feel. But whether you act from the anger, and how, is chosen.

His practical recommendations are simple. First: delay. 'The greatest remedy for anger is delay.' The initial intensity decreases rapidly if you do not feed it. Most things that seem intolerable in the first five minutes look different after an hour.

Second: perspective. Place the incident in context. How large is this, really, against the scale of your life? How will it feel in a year?

Third: self-examination. Before blaming others, ask whether your own conduct has ever been comparable to what you are blaming them for. 'Let us be more gentle in our assessments; we are bad men who correct bad men.' That is not an instruction to excuse wrongdoing. It is an instruction to correct it without contempt."""),

    ("On Progress", "Epictetus",
"""'If you wish to make progress, be content to seem foolish and stupid about externals.'

He was describing what it actually costs to change. Most people want improvement — they want to be calmer, wiser, less reactive, more consistent. What they do not want is the period of awkwardness between the old self and the new one. They do not want to look uncertain when they used to look confident. They do not want to lose arguments they used to win by force of will.

But this period of looking foolish is not avoidable. The man who is genuinely becoming less angry will, for a time, simply not respond in situations that used to produce a response. He will seem passive or slow. The woman who is genuinely becoming less concerned with others' opinions will, for a time, not perform the usual social rituals. She will seem cold or indifferent.

Progress is not a smooth upward curve. It is a series of retreats from the old identity before the new one is fully formed. In that in-between space, you are genuinely neither — not who you were, not yet who you are becoming. This is uncomfortable, and most people retreat back into the familiar pattern.

Epictetus thought the test of genuine commitment to change was whether you could tolerate this period — whether you cared more about actually becoming someone different than about appearing consistent. He was suspicious of people who talked about philosophy publicly while remaining privately unchanged. The point of philosophy was not to have interesting opinions. It was to behave differently as a result of thinking more clearly.

'Never call yourself a philosopher. Just do what follows from what you believe.'"""),

    ("On Purpose", "Marcus Aurelius",
"""'Ask yourself at every moment: is this necessary?'

It sounds like a question about efficiency. Aurelius meant something deeper — a question about purpose. Is what you are doing, thinking, or feeling in service of something that actually matters to you, or is it simply habit, obligation, or distraction?

He applied the question to thought as much as to action. There is a kind of mental activity — rehearsing old grievances, imagining disasters that may never come, working out clever things to say to people who have annoyed you — that is constant but purposeless. It consumes attention without producing anything. Asking 'is this necessary?' in the middle of this kind of thinking is the equivalent of finding that you are walking in circles and stopping.

The companion question was: 'What does this situation actually require?' Not what he wanted to do, not what would be easiest or most comfortable, but what the situation genuinely called for. His role as emperor, as father, as friend — each had requirements, and his job was to meet them clearly and without unnecessary elaboration.

He was not advocating narrowness or joylessness. He read widely, studied philosophy, engaged with people from every background. His question was not 'is this productive?' but 'is this mine?' — is this arising from genuine care, genuine curiosity, genuine necessity, or is it simply filling space?

He did not always succeed. The Meditations are full of the gap between aspiration and performance. But the aspiration itself was clear: a life that was intentional rather than reactive, purposeful rather than drifting, answerable to something real rather than merely responsive to whatever had most recently demanded attention."""),

    ("On Perspective", "Zhuangzi",
"""Zhuangzi told a story about a cook who had such mastery of his craft that when he cut up an ox, his knife never dulled. He did not hack through joints; he found the spaces between them, guided by understanding rather than force. The prince who watched him thought he was watching a performance. The cook said: I am simply following the Tao.

Zhuangzi used stories where other philosophers used arguments, and the stories often work on several levels simultaneously. On the surface, the cook is an example of skill. Deeper down, he is an example of a mind that has stopped imposing its own grid on reality and has learned to perceive what is actually there.

His most persistent theme was the relativity of perspective. What looks large from one angle looks small from another. What seems important in one frame seems trivial in the next. The mushroom that lives for a single morning has no conception of seasons. The chrysalis that lives a season has no conception of years. Their ignorance is not deficient; it is simply a different vantage point.

This is not relativism — the view that no perspective is better than any other. It is an argument for holding your own perspective lightly, for recognising that your current frame of reference is not the only possible one, and that reality is usually larger and stranger than whatever framework you are currently using.

The practical implication is something like humility in perception — a willingness to be surprised, to revise, to find that what seemed useless is actually valuable and what seemed essential is actually optional. 'Uselessness is useful.' The tree that is too gnarled to be lumber lives for a thousand years. The question is always: useful to what, on what timescale, from whose vantage point?"""),

    ("On Liberty", "John Stuart Mill",
"""Mill's central argument in On Liberty is simple and radical: the only legitimate reason for society to limit the freedom of any individual is to prevent harm to others. Not to protect their own good. Not to enforce majority opinion about how people should live. Not to preserve tradition. Only harm to others.

He was writing against two things: the tyranny of governments, and what he called the tyranny of prevailing opinion — the pressure that society exerts on individuals to conform, to think and behave like everyone else, to avoid eccentricity even when it harms no one. He thought this second tyranny was more dangerous than the first, because it operated silently, inside people's heads.

His argument for tolerance of diverse ways of living was not moral relativism. He thought people are the best judges of their own good — they understand their own situation and values better than any observer can. And he thought human progress depends on variety and experiment. If everyone is forced to live the same way, society loses the experiments that might have discovered better ways.

He also made an argument specifically about free speech that remains urgent: the silenced opinion might be true. Even if it is not, the process of engaging with it — of having to defend the prevailing view rather than simply assuming it — is how understanding deepens. An opinion that has never been challenged is held mechanically, as a dead dogma, not as a living truth.

'He who knows only his own side of the case knows little of that.' The value of hearing the strongest version of the opposing view is not just tolerance — it is epistemic. It is how you avoid being wrong without knowing you are wrong."""),

    ("On Pragmatism", "William James",
"""William James invented pragmatism as a method for settling metaphysical disputes, and his insight was deceptively simple: if two propositions lead to exactly the same practical consequences, they have exactly the same meaning. A difference that makes no difference is no difference at all.

Applied to ideas more broadly, pragmatism says: the truth of a belief is not a fixed property it has independent of us, but something that happens to it — a belief is true insofar as it helps us navigate the world, make useful predictions, and live better. This sounds like it makes truth arbitrary. James insisted it did not. The test is not whether a belief makes you feel good but whether it actually works — whether it survives contact with experience, whether it holds up under pressure.

He was particularly interested in the psychology of belief — how we form beliefs, why we hold on to them, what it would take to change them. His observation was that most people do not reason their way to beliefs; they begin with a conviction and then find reasons for it. The reasons feel like causes but are usually justifications after the fact.

The practical implication was to be suspicious of the conviction that comes too easily, that has no memory of the process by which it arrived. Real beliefs should be able to tell you something about how they would be falsified — what it would take to prove them wrong. If a belief cannot answer that question, it is probably not a belief at all but a preference masquerading as one.

'Act as if what you do makes a difference. It does.' This is not naive optimism. It is the pragmatist's response to paralysis: the question of whether your action matters is itself answered by acting."""),

    ("On Epicurean Pleasure", "Epicurus",
"""Epicurus is routinely misunderstood. His name has become synonymous with luxury and sensual indulgence — 'epicurean' now means someone who enjoys fine food and wine. The real Epicurus lived on bread, olives, and water, and thought this was living well.

His philosophy was about pleasure, but he distinguished between two kinds. Kinetic pleasures are the active pleasures of desire being satisfied — eating when hungry, drinking when thirsty, pursuing and obtaining what you want. These are real pleasures, but they are inherently unstable. Desire, once satisfied, is replaced by new desire. The pleasure is inseparable from the prior lack.

Katastematic pleasures are different — they are the stable pleasures of a state of contentment. Not the satisfaction of a desire, but the absence of pain and anxiety. Ataraxia: tranquility, equanimity, the condition of a person who wants what they have rather than chasing what they do not. This was, for Epicurus, the highest pleasure available to a human being.

The practical implications were radical. Stop pursuing things you do not need. Examine which of your desires are natural and necessary, which are natural but unnecessary, and which are neither. The first category is small: enough food, safety, friendship, some shelter from the elements. Everything beyond this is a trap — it produces the anxiety of wanting it, the risk of losing it, and the disappointment of discovering it did not satisfy as much as expected.

He also insisted on friendship as essential. 'Of all the things that wisdom provides for living one's whole life in happiness, the greatest by far is the possession of friendship.' Not a decorative addition to life but a central necessity."""),

    ("On Freedom from Convention", "Diogenes",
"""Diogenes of Sinope was thrown out of his home city for defacing the coinage — literally, stamping false currency. He spent the rest of his life defacing figurative currency: the conventions, pretensions, and social performances that pass for respectability.

He slept in a large ceramic jar. He ate in the marketplace, which was considered obscene. When Alexander the Great came to visit him and asked if there was anything he needed, Diogenes said: yes, stand out of my sunlight. He saw no reason to treat power with reverence it had not earned.

His philosophy was called cynicism — from the Greek word for dog — because he and his followers lived with what they considered the simplicity and honesty of animals, without the elaborate social performances of human beings. The dog does not pretend to be better than it is. The dog does not perform wealth or status. The dog does what it does and sleeps when it sleeps.

He was not advocating for actual animal life. He was using the dog as a provocation — a way of asking which human conventions are genuinely valuable and which are merely performances of value. The toga that marks you as respectable. The titles that must be used. The places where certain things may or may not be said or done.

Diogenes thought most of these conventions were forms of slavery — that people accepted enormous constraints on their behaviour in exchange for social approval that was itself worth very little. His freedom was the freedom of someone who has genuinely stopped caring what others think, because he had examined the matter and decided their opinions were not worth the price of their approval.

He was extreme. He was also, occasionally, correct."""),

    ("On Friendship", "Aristotle",
"""Aristotle devoted more pages of the Nicomachean Ethics to friendship than to any other single topic. He thought it was not a decoration on the good life but a constituent of it — you cannot live well without genuine friends.

He distinguished three kinds. Friendships of utility exist because each party gets something useful from the other — business relationships, convenient acquaintances, people we like because they are helpful. Friendships of pleasure exist because each party enjoys the other's company — the fun of spending time together, shared interests, good humour. Both of these kinds of friendship are real, but they are contingent. The friendship lasts as long as the utility or the pleasure does.

The third kind — friendship of character, or complete friendship — is rarer and more demanding. It is the friendship between people who admire each other's virtue, who wish each other well for the other's own sake, who are engaged in something like a long-running conversation about how to live well. This kind of friendship survives the removal of all benefits, because the benefit was never the point.

He also thought that genuine self-knowledge was almost impossible without this kind of friend. We are not good judges of our own character — we tend to think better of ourselves than we deserve, to miss our own blind spots, to mistake our weaknesses for strengths. A real friend who knows you well and wishes you well is one of the few sources of honest feedback that actually reaches you.

This is why the person who has many acquaintances and no real friends is, in Aristotle's view, in a worse epistemic position than they know. They have lost the main mechanism by which character is examined and refined."""),

    ("On Love", "Plato",
"""In Plato's Symposium, a series of characters give speeches in praise of love, each from a different angle. The most famous is Aristophanes' myth: that human beings were originally spherical creatures with four arms, four legs, and two faces, and that the gods split them in half. Love is the search for the other half, the longing to be complete.

Socrates, in his speech, says he learned about love from a priestess named Diotima — and what she told him was more demanding. Love, she said, is not the possession of beauty but the desire for it. A person who is beautiful does not love beauty; a person who has wisdom does not seek wisdom. It is the lack that drives the seeking.

But she went further. The lover begins by loving a beautiful body. A more advanced lover recognises that the beauty in one body is kin to the beauty in all bodies, and begins to love beauty more generally. A still more advanced lover recognises that the beauty of souls is greater than the beauty of bodies, and begins to love beautiful minds and characters. Eventually — and this is the culmination of her argument — the lover catches a glimpse of beauty itself, not in any particular body or mind, but the form of beauty, pure and unchanging.

Whether you accept this metaphysical structure or not, the movement it describes is real: from the particular to the general, from the specific to the principle, from the beloved person to the thing that made them loveable. What begins as attachment becomes, at its furthest reach, something like philosophical wonder.

Love, for Plato, is not just an emotion. It is an epistemological engine."""),

    ("On Death", "Socrates",
"""When the jury sentenced Socrates to death, he delivered what is arguably the most extraordinary response to a death sentence in recorded history. He did not beg. He did not recant. He said, essentially: you have freed me.

His argument was characteristically precise. Death is one of two things: either an endless dreamless sleep — in which case it is nothing to fear, since we do not suffer from the nights in which we do not dream — or a journey to another place, where the souls of all who have died have gone before. If the latter, then what an extraordinary opportunity: to finally meet Homer, Hesiod, the heroes of Troy, all the great thinkers and poets, and to spend eternity in conversation with them about what actually matters.

Either way, he could not see the harm. The worst they could do to him, it turned out, was to accelerate something that was going to happen anyway, and save him from the difficulties of old age.

He was not performing courage. He genuinely believed that the care of the soul was the only thing worth spending a life on, and that a philosopher who had done this had nothing to fear in death. The fear of death, he thought, was a kind of pretending to know something you do not know — assuming that death is bad without any actual knowledge of what it is.

The last thing he said, as the hemlock took effect, was a request that a friend sacrifice a rooster to Asclepius, the god of medicine. It was the conventional offering made when someone recovered from a disease. He was indicating that death, for him, was a cure."""),

    ("On Civil Disobedience", "Henry David Thoreau",
"""In 1846, Thoreau spent a night in jail rather than pay his poll tax to a government that supported slavery and was conducting a war he considered unjust. It was a single night — a friend paid the tax on his behalf — but the experience produced one of the most influential political essays in American history.

His argument was direct: when a government enacts unjust laws, the obligation of a just person is not to wait for the political process to correct them. It is to refuse to comply with them, immediately, regardless of consequence. 'Under a government which imprisons any unjustly, the true place for a just man is also a prison.'

He was suspicious of people who agreed with him in principle but did not act. They voted against slavery; they wrote letters; they signed petitions. Meanwhile, they paid their taxes and kept the machine running. The man who votes correctly but whose life and money continues to support the wrong is still, in effect, supporting it. Good intentions without changed behaviour are not enough.

What he was describing was a politics of personal integrity — the insistence that the state's authority over you ends where your conscience begins. This is not a comfortable position. It requires actually bearing the costs of disagreement rather than merely performing disagreement.

His essay influenced Gandhi's development of satyagraha, and through Gandhi it influenced the American civil rights movement. Martin Luther King read Thoreau as a student. The argument is still active, still demanding the same question: at what point is compliance complicity?"""),

    ("On Nature", "Ralph Waldo Emerson",
"""Emerson's first book was called Nature, and it began a tradition of American thought that tried to find in the natural world something that organised religion no longer provided: a direct encounter with the divine.

His central claim was that nature is not merely backdrop — the scenery behind human drama — but a living symbol of something larger. Every natural fact, he thought, is a symbol of some spiritual fact. The structure of a tree, the motion of a river, the fact of seasons — these are not just physical events but expressions of laws that also govern human life and thought.

He was partly arguing against a kind of urban self-enclosure — the tendency of modern life to cut itself off from the natural world entirely and to become entirely absorbed in human affairs. This produced, he thought, a diminishment. People who never spent time in genuine nature were missing a recalibration available nowhere else.

But his deeper argument was about receptivity. The experience of nature — if you are actually paying attention, if you have allowed yourself to be quiet enough to receive it — can produce what he called an 'original relation to the universe.' Not a relation mediated by tradition, education, or doctrine, but a direct one. This was what he meant by the transparent eyeball: the moment in which the self seems to dissolve and you are simply part of the whole, seeing through you rather than being seen by you.

You do not need to share his metaphysics to recognise what he is pointing at. There is something available in genuine attention to the natural world that is not available anywhere else, and most of us are not getting enough of it."""),

    ("On Eternal Recurrence", "Friedrich Nietzsche",
"""The strangest idea Nietzsche ever had was also his most personal: the eternal recurrence. Suppose, he wrote, that you will live this life again — not a different life but this exact one, with every pleasure and every pain, every joy and every humiliation, repeated endlessly. Could you affirm it? Would you want it?

He introduced it as a thought experiment, not a cosmological claim. He was not seriously arguing that physics would produce an infinite repetition of identical universes. He was using the thought experiment as a test — a way of asking how you feel about your life, stripped of the comfort that it will eventually end.

Most people get through their lives by reassuring themselves that things will be different. The bad parts will pass. Someday they will be in a better situation, a better mood, a better relationship. The eternal recurrence removes this reassurance. If every moment returns infinitely, the question is whether you can say yes to each one — including the ones you hate, including the ones that have been taken from you, including the ones that have broken you.

The person who could sincerely say yes — who could embrace the eternal recurrence of their own life — would be someone who had achieved what Nietzsche called amor fati: the love of fate. Not resignation to fate, not mere acceptance, but genuine love — the kind that does not wish anything had been otherwise, because you understand that everything that happened is part of what made you who you are.

This is a very high standard. Nietzsche knew that. He also knew that the alternative — the life lived half-heartedly, in perpetual postponement — was a much worse kind of failure."""),

    ("On Happiness", "Bertrand Russell",
"""Russell's 'Conquest of Happiness' is unusual among philosophical treatments of its subject because it is relentlessly practical. He was not interested in defining happiness or locating its ultimate ground. He wanted to know what actually makes people miserable, and what can be done about it.

His diagnosis of unhappiness is specific. Excessive self-preoccupation is at the top of his list — the habit of turning inward and examining your own thoughts and feelings with too much attention, too much anxiety about whether they are correct, too much concern with how you appear to yourself. This is the condition he called 'the disease of self.' The person in its grip spends enormous energy on internal accounting that produces diminishing returns.

His remedy is equally specific: get genuinely interested in something outside yourself. Not as a technique for feeling better, but as a genuine reorientation. The person who is absorbed in a problem — scientific, artistic, political, personal — is not performing interest as a cure for misery. They have simply found something that matters more than their own mood.

He also wrote about the importance of what he called 'impersonal interests' — things you care about that are not about you at all. History, mathematics, astronomy, music, the lives of people you will never meet. These provide what he called a refuge from the self, a way of being connected to something that will persist long after your personal concerns have resolved or dissolved.

'The good life,' he concluded, 'is one inspired by love and guided by knowledge.' Love expands the self; knowledge situates it. Together they make possible a kind of happiness that does not depend on circumstances being particularly favourable."""),

    ("On Service", "Marcus Aurelius",
"""There is a particular passage in the Meditations that does not get enough attention. Aurelius writes that when you wake up in the morning and find it difficult to get up, you should say to yourself: 'I am rising to the work of a human being. Why should I complain of my nature if it is the nature of a human being to do his work?'

He was an emperor who found it difficult to get out of bed. This is, in some ways, the most human thing about him. The point is what he did with it: not self-recrimination, not elaborate motivation techniques, but a simple appeal to function. This is what you are here to do. Do it.

His Stoic framework held that human beings have a natural function — the same way a hand has a function, or an eye. The function of a human being is rational action in community with other human beings. To fulfil this function is to live well; to fail at it is to live poorly, regardless of how comfortable the failure is.

Service, in this account, is not a sacrifice that the virtuous person makes. It is the natural expression of what a human being is for. The person who retreats entirely from the world and its demands has not achieved freedom — they have simply failed to be fully human.

He also made the practical point that service done with resentment is worse than useless. If you are going to act for others — as emperor, as father, as friend — the quality of the action depends on the quality of the attention behind it. Do it fully, or do not do it."""),
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

# ── Pick today's reading (weighted) ──────────────────────────────────────────
try:
    with open("passages_state.json", "r", encoding="utf-8") as f:
        passages_state = json.load(f)
except FileNotFoundError:
    passages_state = {}

def passage_weight(idx):
    last = passages_state.get(str(idx), {}).get("last_sent")
    if not last:
        return 1.0
    weeks = (date.today() - datetime.fromisoformat(last).date()).days // 7
    return min(1.0, weeks / DECAY_WEEKS)

p_weights = [passage_weight(i) for i in range(len(PASSAGES))]
chosen_passage_idx = random.choices(range(len(PASSAGES)), weights=p_weights, k=1)[0]
passage_title, passage_author, passage_text = PASSAGES[chosen_passage_idx]
passage_html = passage_text.strip().replace('\n\n', '<br><br>')

# ── Pick today's chess lesson ─────────────────────────────────────────────────
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
    passages_state[str(chosen_passage_idx)] = {"last_sent": today_str}
    with open("passages_state.json", "w", encoding="utf-8") as f:
        json.dump(passages_state, f, ensure_ascii=False, indent=2)

# ── Execute ───────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    send_email()
    mark_as_sent()
