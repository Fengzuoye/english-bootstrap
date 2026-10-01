# 第 0 层：核心基础词表（公理层）

> 本层是英语自举的“公理层”：这些词不给出英语定义，直接记忆。
> 中文速记只在本层出现一次，是入口拐杖；从第 1 层起，所有新词一律只用
> “第 0 层 + 之前已定义词”的英语来定义，例句也一样。
> 本文件是机器可读的：`tools/check.py` 直接从下面各表读取词表。

## 使用说明

1. **一个词条 = 一个词**。一词多义不拆开（如 `like` 既指“像”也指“喜欢”），
   义项在语法层和词汇层逐步展开。
2. **形态变化不算新词**：`I/me/my`、`book/books`、`go/went/gone` 都算同一个词，
   由第 1 层语法处理；检查器会自动归并常见词形变化。
3. **拼写以美式为准**（`color`）；英式变体（`colour`）视为同一个词。
4. 本层所有词都落在 Oxford 3000 之内（基本都在最常用的前 1500 词里）。

## 统计

| 类别 | 数量 |
|---|---:|
| 代词 | 18 |
| 冠词 | 3 |
| 数词 | 11 |
| 限定词/数量 | 12 |
| 基本名词 | 37 |
| 基本动词 | 39 |
| 基本形容词 | 27 |
| 基本副词 | 11 |
| 介词 | 17 |
| 连词/疑问词 | 12 |
| 助动词/情态 | 8 |
| 感叹词 | 6 |
| **核心合计** | **201** |

## 1. 代词（18）

| 词 | 词性 | 中文速记（仅本层） |
|---|---|---|
| I | pronoun | 我 |
| you | pronoun | 你；你们 |
| he | pronoun | 他 |
| she | pronoun | 她 |
| it | pronoun | 它；指已提到的事物 |
| we | pronoun | 我们 |
| they | pronoun | 他们/她们/它们 |
| who | pronoun | 谁；（从句）…的人 |
| what | pronoun | 什么 |
| which | pronoun | 哪一个 |
| someone | pronoun | 某人 |
| something | pronoun | 某物；某事 |
| this | pronoun | 这；这个 |
| that | pronoun | 那；那个；（从句）那个… |
| these | pronoun | 这些（this 的复数） |
| those | pronoun | 那些（that 的复数） |
| other | pronoun | 另一个；其他的 |
| same | pronoun | 相同的；同样的事物 |

## 2. 冠词（3）

| 词 | 词性 | 中文速记（仅本层） |
|---|---|---|
| a | article | 一个（用于辅音音前） |
| an | article | 一个（用于元音音前，a 的变体） |
| the | article | 这；那（特指） |

## 3. 数词（11）

| 词 | 词性 | 中文速记（仅本层） |
|---|---|---|
| zero | number | 零 |
| one | number | 一；一个（也可作代词，代替前面提到的事物） |
| two | number | 二 |
| three | number | 三 |
| four | number | 四 |
| five | number | 五 |
| six | number | 六 |
| seven | number | 七 |
| eight | number | 八 |
| nine | number | 九 |
| ten | number | 十 |

> 十以上的数词（eleven、hundred…）将在后续层用 one 到 ten 递归定义
> （eleven = ten and one；hundred = ten tens）。序数词（first、second…）由第 1 层语法处理。

## 4. 限定词/数量（12）

| 词 | 词性 | 中文速记（仅本层） |
|---|---|---|
| all | determiner | 所有；全部 |
| some | determiner | 一些；某个 |
| any | determiner | 任何；一些（多用于否定/疑问） |
| each | determiner | 每个 |
| every | determiner | 每一个（强调整体） |
| many | determiner | 许多（可数） |
| much | determiner | 许多（不可数） |
| more | determiner | 更多；更 |
| most | determiner | 最多；大多数 |
| few | determiner | 很少（可数） |
| little | determiner | 很少（不可数）；小的 |
| less | determiner | 更少 |

## 5. 基本名词（37）

| 词 | 词性 | 中文速记（仅本层） |
|---|---|---|
| thing | noun | 东西；事情 |
| person | noun | 人（个体） |
| people | noun | 人们（person 的复数） |
| body | noun | 身体 |
| place | noun | 地方 |
| time | noun | 时间；次数 |
| day | noun | 天；白天 |
| night | noun | 夜晚 |
| year | noun | 年 |
| way | noun | 方法；方式；路 |
| part | noun | 部分 |
| kind | noun | 种类 |
| group | noun | 群；组 |
| word | noun | 词 |
| name | noun | 名字 |
| number | noun | 数字；数量 |
| side | noun | 边；侧 |
| water | noun | 水 |
| fire | noun | 火 |
| air | noun | 空气 |
| earth | noun | 地球；大地；土 |
| sun | noun | 太阳 |
| moon | noun | 月亮 |
| sky | noun | 天空 |
| food | noun | 食物 |
| hand | noun | 手 |
| head | noun | 头 |
| eye | noun | 眼睛 |
| animal | noun | 动物 |
| man | noun | 男人；人（泛称） |
| woman | noun | 女人 |
| husband | noun | 丈夫 |
| wife | noun | 妻子 |
| child | noun | 孩子 |
| family | noun | 家庭；家人 |
| money | noun | 钱 |
| color | noun | 颜色 |

## 6. 基本动词（37）

| 词 | 词性 | 中文速记（仅本层） |
|---|---|---|
| be | verb | 是；存在；处于（某状态） |
| have | verb | 有；拥有 |
| do | verb | 做；（构成否定/疑问） |
| say | verb | 说 |
| tell | verb | 告诉 |
| ask | verb | 问；请求 |
| think | verb | 想；认为 |
| know | verb | 知道 |
| want | verb | 想要 |
| feel | verb | 感觉；摸 |
| see | verb | 看见 |
| hear | verb | 听见 |
| mean | verb | 意思是 |
| happen | verb | 发生 |
| need | verb | 需要 |
| go | verb | 去 |
| come | verb | 来 |
| move | verb | 移动 |
| make | verb | 做；制造 |
| give | verb | 给 |
| get | verb | 得到；变得 |
| take | verb | 拿；带走；花费（时间） |
| use | verb | 使用 |
| touch | verb | 触摸 |
| open | verb | 打开 |
| close | verb | 关闭 |
| start | verb | 开始 |
| stop | verb | 停止 |
| live | verb | 住；活 |
| look | verb | 看；看起来 |
| die | verb | 死 |
| eat | verb | 吃 |
| drink | verb | 喝 |
| sleep | verb | 睡觉 |
| work | verb | 工作；（机器）运转 |
| play | verb | 玩；播放 |
| put | verb | 放；放置 |
| stand | verb | 站 |
| sit | verb | 坐 |

## 7. 基本形容词（27）

| 词 | 词性 | 中文速记（仅本层） |
|---|---|---|
| good | adjective | 好的 |
| bad | adjective | 坏的 |
| big | adjective | 大的 |
| small | adjective | 小的 |
| long | adjective | 长的 |
| short | adjective | 短的；矮的 |
| fast | adjective | 快的；迅速的 |
| high | adjective | 高的 |
| low | adjective | 低的 |
| new | adjective | 新的 |
| old | adjective | 老的；旧的 |
| hot | adjective | 热的 |
| cold | adjective | 冷的 |
| true | adjective | 真的；真实的 |
| right | adjective | 对的；正确的；右边 |
| hard | adjective | 硬的；困难的 |
| near | adjective | 近的 |
| different | adjective | 不同的 |
| empty | adjective | 空的 |
| black | adjective | 黑色的 |
| white | adjective | 白色的 |
| red | adjective | 红色的 |
| yellow | adjective | 黄色的 |
| green | adjective | 绿色的 |
| blue | adjective | 蓝色的 |
| brown | adjective | 棕色的 |
| married | adjective | 已婚的 |

## 8. 基本副词（11）

| 词 | 词性 | 中文速记（仅本层） |
|---|---|---|
| not | adverb | 不；没有 |
| very | adverb | 非常 |
| too | adverb | 也；太 |
| also | adverb | 也 |
| only | adverb | 只；仅仅 |
| now | adverb | 现在 |
| here | adverb | 这里 |
| there | adverb | 那里；（there is/are）有 |
| yes | adverb | 是（肯定回答） |
| no | adverb | 不（否定回答）；没有 |
| maybe | adverb | 也许 |

## 9. 介词（17）

| 词 | 词性 | 中文速记（仅本层） |
|---|---|---|
| in | preposition | 在…里面 |
| on | preposition | 在…上面 |
| at | preposition | 在（某点/时刻/地点） |
| to | preposition | 到；向；给（方向/对象） |
| from | preposition | 从；来自 |
| of | preposition | …的（所属/部分） |
| for | preposition | 为了；给；持续（时间） |
| with | preposition | 和…一起；用（工具） |
| by | preposition | 通过；由；在…旁边 |
| about | preposition | 关于；大约 |
| as | preposition | 作为；像；当…时 |
| like | preposition | 像（也作动词：喜欢） |
| after | preposition | 在…之后 |
| before | preposition | 在…之前 |
| under | preposition | 在…下面 |
| over | preposition | 在…上方；超过 |
| between | preposition | 在…之间 |

## 10. 连词/疑问词（11）

| 词 | 词性 | 中文速记（仅本层） |
|---|---|---|
| and | conjunction | 和；而且 |
| or | conjunction | 或；否则 |
| but | conjunction | 但是 |
| if | conjunction | 如果；是否 |
| because | conjunction | 因为 |
| so | conjunction | 所以；如此 |
| when | conjunction | 什么时候；当…时 |
| where | conjunction | 哪里；（在）…的地方 |
| why | conjunction | 为什么 |
| how | conjunction | 怎样；多么 |
| than | conjunction | 比 |
| whose | conjunction | 谁的 |

## 11. 助动词/情态（8）

| 词 | 词性 | 中文速记（仅本层） |
|---|---|---|
| can | modal | 能；可以 |
| could | modal | 能；可以（can 的委婉/过去式） |
| may | modal | 可以；可能 |
| might | modal | 可能；也许（may 的委婉式） |
| must | modal | 必须 |
| will | modal | 将；（表意愿） |
| would | modal | 会（委婉/过去将来） |
| should | modal | 应该 |

## 12. 感叹词（6）

| 词 | 词性 | 中文速记（仅本层） |
|---|---|---|
| oh | interjection | 哦；啊（感叹） |
| please | interjection | 请 |
| sorry | interjection | 对不起；抱歉 |
| thanks | interjection | 谢谢 |
| hello | interjection | 你好 |
| goodbye | interjection | 再见 |

## 可降级清单（想更精简时可移到第 1 层）

下面 33 个词其实**可以用第 0 层其他词直接定义**，但因为太常用，默认留在第 0 层。
如果想把第 0 层压到最小，就把它们移出，放进第 1 层的第一批定义里（严格核心 ≈ 168 词）。
清单里的定义都只用第 0 层词，已按依赖顺序排列。

"few" is a determiner. The meaning of "few" is "not many".
"little" is a determiner. The meaning of "little" is "not much".
"most" is a determiner. The meaning of "most" is "more than all the other ones".
"less" is a determiner. The meaning of "less" is "not so much".
"zero" is a number. The meaning of "zero" is "the number before one".
"two" is a number. The meaning of "two" is "one and one".
"three" is a number. The meaning of "three" is "two and one".
"four" is a number. The meaning of "four" is "three and one".
"five" is a number. The meaning of "five" is "four and one".
"six" is a number. The meaning of "six" is "five and one".
"seven" is a number. The meaning of "seven" is "six and one".
"eight" is a number. The meaning of "eight" is "seven and one".
"nine" is a number. The meaning of "nine" is "eight and one".
"ten" is a number. The meaning of "ten" is "nine and one".
"sound" is a noun. The meaning of "sound" is "something that you hear".
"world" is a noun. The meaning of "world" is "the earth and all people and things on it".
"hand" is a noun. The meaning of "hand" is "the part of the body that you use to take things".
"head" is a noun. The meaning of "head" is "the part of the body that has the eyes in it".
"eye" is a noun. The meaning of "eye" is "the part of the body that you see with".
"animal" is a noun. The meaning of "animal" is "a thing with a body that moves and feels".
"money" is a noun. The meaning of "money" is "the thing that people give to get other things".
"go" is a verb. The meaning of "go" is "move from this place to other places".
"come" is a verb. The meaning of "come" is "move to this place".
"give" is a verb. The meaning of "give" is "make someone have something".
"get" is a verb. The meaning of "get" is "come to have".
"take" is a verb. The meaning of "take" is "have something with you when you go".
"close" is a verb. The meaning of "close" is "make something not open".
"use" is a verb. The meaning of "use" is "do something with a thing".
"put" is a verb. The meaning of "put" is "make something be in a place".
"look" is a verb. The meaning of "look" is "use your eyes to see something".
"near" is an adjective. The meaning of "near" is "at a short way from".
"empty" is an adjective. The meaning of "empty" is "with no thing in it".
