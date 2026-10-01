# 第 1 层预热（机制演示，不是正式层）

> 这一页只做一件事：证明“只用第 0 层 201 个词就能定义新词”。
> 每个条目都经过 `tools/check.py --preview` 校验。
> 正式的第 1 层会先讲词性和最基础语法，再系统定义这些词（以及更多）。

## 格式说明

- 第 0 层之后，每个新词都用同样的三句话解释：
  - "word" is a noun.
  - The meaning of "word" is "...".
  - Example: "..."
- 模板句（The meaning of ... is / Example:）是固定格式，不参与词汇检查；
  只有引号里的定义和例句才接受检查。
- 例句里的词形变化（comes/words…）不算新词。
- 这些定义按文件内顺序依赖前面已经定义的词。

## 第一批：由 not / 方向 / 比较 直接推出

"out" is an adverb.
The meaning of "out" is "not in".
Example: "He is out."

"up" is an adverb.
The meaning of "up" is "to a high place".
Example: "The sun is up."

"down" is an adverb.
The meaning of "down" is "to a low place".
Example: "Come down."

"into" is a preposition.
The meaning of "into" is "to in".
Example: "He goes into the water."

"without" is a preposition.
The meaning of "without" is "not with".
Example: "I can live without water."

"slow" is an adjective.
The meaning of "slow" is "not fast".
Example: "You are slow."

"easy" is an adjective.
The meaning of "easy" is "not hard".
Example: "This is easy."

"wrong" is an adjective.
The meaning of "wrong" is "not right".
Example: "That is wrong."

"full" is an adjective.
The meaning of "full" is "not empty".
Example: "The day is full of work."

## 第二批：名词

"sound" is a noun.
The meaning of "sound" is "something that you hear".
Example: "I hear a sound."

"world" is a noun.
The meaning of "world" is "the earth and all people and things on it".
Example: "The world is big."

## 第三批：动作与关系

"love" is a verb.
The meaning of "love" is "like very much".
Example: "I love you."

"friend" is a noun.
The meaning of "friend" is "a person that you like and that likes you".
Example: "I have a friend."

"buy" is a verb.
The meaning of "buy" is "get something with money".
Example: "I buy food with money."

"sell" is a verb.
The meaning of "sell" is "give something for money".
Example: "He sells food for money."

"speak" is a verb.
The meaning of "speak" is "say words".
Example: "I speak to you."

"read" is a verb.
The meaning of "read" is "see words and know what they say".
Example: "I read words."

"write" is a verb.
The meaning of "write" is "make words that people can see".
Example: "I write words."

"help" is a verb.
The meaning of "help" is "do something for someone who needs it".
Example: "I help the old man."

## 第四批：时间

"again" is an adverb.
The meaning of "again" is "one more time".
Example: "Say it again."

"always" is an adverb.
The meaning of "always" is "at all times".
Example: "The sun always comes up."

"never" is an adverb.
The meaning of "never" is "not at any time".
Example: "I never sleep in the day."

"soon" is an adverb.
The meaning of "soon" is "after a short time".
Example: "We will eat soon."

"then" is an adverb.
The meaning of "then" is "at that time".
Example: "I eat now, and then I sleep."

"another" is a determiner.
The meaning of "another" is "one more".
Example: "I want another one."

## 第五批：情感与状态

"happy" is an adjective.
The meaning of "happy" is "feeling good".
Example: "I am happy."

"sad" is an adjective.
The meaning of "sad" is "feeling bad".
Example: "She is sad."

"afraid" is an adjective.
The meaning of "afraid" is "feeling bad because something bad may happen".
Example: "I am afraid of water."

"angry" is an adjective.
The meaning of "angry" is "feeling bad because someone did a bad thing to you".
Example: "The man is angry."

## 第六批：性质

"wet" is an adjective.
The meaning of "wet" is "with water on it".
Example: "He is wet."

"dry" is an adjective.
The meaning of "dry" is "not wet".
Example: "The earth is dry."

"far" is an adjective.
The meaning of "far" is "a long way from here".
Example: "The moon is far from the earth."

"rich" is an adjective.
The meaning of "rich" is "with much money".
Example: "He is a rich man."

"poor" is an adjective.
The meaning of "poor" is "with no money".
Example: "She is a poor woman."

"strong" is an adjective.
The meaning of "strong" is "can do hard things".
Example: "I am strong."

"weak" is an adjective.
The meaning of "weak" is "not strong".
Example: "The old man is weak."

"young" is an adjective.
The meaning of "young" is "not old".
Example: "The child is young."

"beautiful" is an adjective.
The meaning of "beautiful" is "very good to see".
Example: "The sky is beautiful."

"ugly" is an adjective.
The meaning of "ugly" is "not good to see".
Example: "The color is ugly."

## 第七批：动作

"wake" is a verb.
The meaning of "wake" is "stop sleeping".
Example: "He wakes at night."

"begin" is a verb.
The meaning of "begin" is "start".
Example: "The day begins with the sun."

"end" is a verb.
The meaning of "end" is "stop".
Example: "The day ends at night."

"laugh" is a verb.
The meaning of "laugh" is "make a sound because you are happy".
Example: "The child laughs."

"cry" is a verb.
The meaning of "cry" is "make a sound because you feel bad".
Example: "The child cries."
