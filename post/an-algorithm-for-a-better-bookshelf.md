```
Date: 2025.06.30
Author: Erica Klarreich
Source: https://cacm.acm.org/news/an-algorithm-for-a-better-bookshelf/
```

# An Algorithm for a Better Bookshelf: Managing the strategic positioning of empty spaces.

Drop in at a library, and you’ll likely notice that most shelves aren’t full—librarians leave some empty space on each shelf. That way, when they get new books, they can slot them into place without having to move too many other books.

It’s a simple-enough idea, but one that arises in a host of settings in computer science that involve sorted data, such as an alphabetically ordered census repository, or a list of connections between members of a social network. In such situations, where the entries can number in the hundreds of billions, the strategic positioning of empty spaces takes on great significance.

“Problems are getting bigger and bigger as we get more and more data,” said Helen Xu, an assistant professor in the School of Computational Science and Engineering at the Georgia Institute of Technology (Georgia Tech) in Atlanta. “At these scales, it becomes important to efficiently manage how you add new entries.”

The bookshelf problem (which computer scientists call the “list labeling” problem) is one of the most basic topics in the field of data structures. “It’s the kind of problem you’d teach to freshman or sophomore undergraduates,” said Guy Blelloch, a professor of computer science at Carnegie Mellon University in Pittsburgh.

Yet until recently, there was a wide gap between what computer scientists could achieve algorithmically and what they knew about the theoretical lower limit on how many books you should expect to have to move when a new book arrives. On the algorithmic side, “There was pretty much no progress for 30 years or more,” Blelloch said.

Now, researchers have come up with a new algorithm that comes close to that theoretical lower limit. Blelloch described it as “a very elegant result.”

The new approach will “hopefully open the door to new applications of list labeling in settings where it wasn’t useful before because the cost was infeasible,” said William Kuszmaul, an assistant professor of computer science at Carnegie Mellon University and one of the researchers who came up with the new algorithm.

The list labeling problem starts off with a bookshelf of size *n*, along with some upper limit—say, 75% or 90%—for how much of the bookshelf you’re allowed to fill. There’s some chosen ordering for books (say, alphabetical by author), and as books arrive, one by one, you choose spots for them that respect the ordering, moving other books as needed. To find book-placing algorithms that are robust under many different conditions, computer scientists imagine that the books are being sent by an adversary who knows the algorithm and is trying to force you to move as many books as possible. (In some versions of the problem, the adversary may also remove books.)

If you were to use the most naïve possible algorithm—the one that places each book as close as possible to the start of the bookshelf—then your adversary could force you to move every book you’ve placed so far, simply by sending you books that precede every book they’ve already sent. As the bookshelf fills up, the cost of accommodating new books becomes proportional to *n*.

In 1981, computer scientists came up with a much better algorithm, whose average cost for adding a new book is only about log<sup>2</sup>*n*. This algorithm starts by dividing the bookshelf into two equal chunks; then it divides each of those chunks in half, and so on. For each different size scale, the algorithm sets a threshold for how full the chunks of that size are allowed to be, with small chunks allowed to be fuller than large chunks. Once the books start arriving, if a new book pushes some chunk over its density threshold, the algorithm spreads out the books in the next larger chunk so they are evenly spaced, easing the pressure on the smaller chunk.

In the years that followed, researchers came up with variations on the theme of spreading books out evenly—“smooth” algorithms, as they’re called. However, no one could beat the log<sup>2</sup>*n* cost of the 1981 algorithm. In 1990, computer scientists proved that no smooth algorithm can do better than log<sup>2</sup>*n*. Still, it didn’t seem to make sense to switch to a non-smooth algorithm—after all, if your algorithm intentionally creates spots that are denser than average, your adversary can target those spots and force you to move a lot of books.

“The running belief seemed to become that log<sup>2</sup>*n* should be optimal, and that what we should be doing as a community is trying to prove it,” said Kuszmaul.

The focus shifted from looking for new algorithms to proving lower bounds for wider and wider classes of algorithms. In 2012, researchers proved that no deterministic algorithm can improve on log<sup>2</sup>*n*. “It’s amazing how strong and robust that bound is,” said Michael Bender, of Stony Brook University, one of the authors of the new paper.

Combined with the earlier results, “This meant that to beat log<sup>2</sup>*n*, you had to be both randomized and non-smooth, and you had to do both things in a meaningful way,” Kuszmaul said.

The first glimmer of how to achieve this came from an unexpected direction: privacy research. In 2016, Bender and other researchers astonished computer scientists by showing that it is possible to create a bookshelf algorithm with a property called “history independence” without worsening the log<sup>2</sup>*n* cost. An algorithm is history-independent if the current state of the bookshelf reveals nothing about the prior history of insertions and deletions, apart from showing which books are currently on the shelf.

Bender and his colleagues had created their history-independent algorithm for the sake of its security properties, but they gradually realized that history independence could also offer algorithmic advantages. With a history-independent algorithm, an adversary can’t use some clever ordering of insertions to influence where dense hotspots will appear—no matter the ordering, the bookshelf will end up looking the same. This feature simplifies the collection of potential dangers against which the algorithm must guard.

In 2022, Bender, Kuszmaul, and colleagues figured out how to make a history-independent algorithm that incurs a cost per book of only log<sup>1.5</sup>*n*, breaking the four-decades-long dry spell. Their algorithm modified the 2016 algorithm to make it more “lazy,” as Kuszmaul put it—the algorithm doesn’t rush to smooth out vulnerable dense spots. Next, the researchers added a layer of randomness to the shelving process to hide the location of these dense spots, so the adversary can’t target them.

The researchers also proved their result was sharp: no history-independent algorithm can do better than log<sup>1.5</sup>*n*. Many computer scientists guessed, therefore, that this new algorithm was the final answer to the bookshelf problem. “We thought it was probably the end of the road,” Kuszmaul said.

Yet laziness is only one of two desirable properties for a bookshelf algorithm. There’s a second property that is fundamentally incompatible with history independence: the ability to proactively respond to an adversary’s strategy.

If the adversary is targeting a particular region, you’d like to quickly move free spots to that area to accommodate incoming books. Yet “If you just do that naively, you are dead in the water,” Kuszmaul said. “The adversary will figure out what you’re doing, and change their behavior to screw you up.”

Now, in a paper posted online in May 2024, Bender, Kuszmaul, and five colleagues have managed to combine the laziness benefits of history independence with a more proactive response to an adversary’s strategy. Their new algorithm adapts to an adversary’s strategy, but on time scales that it picks randomly. “It’s unpredictable enough that the adversary can’t exploit it,” Kuszmaul said. The algorithm “gets the best of both worlds—it behaves morally like a history-independent algorithm, except in the one way it’s being strategically adaptive.”

The new algorithm has an expected cost of log*n* × (log(log*n*))<sup>2</sup> per insertion, a huge improvement on log<sup>1.5</sup>*n*. For large values of *n*, the log*n* factor dwarfs the (log(log*n*))<sup>2</sup> factor, meaning that the cost is only slightly greater than log*n*, which computer scientists have long known is a theoretical lower limit for any bookshelf algorithm.

The improved cost might make the new algorithm—or a simplified version of it—valuable in new data applications, Xu said. Even though many real-world data settings are not adversarial, situations without an adversary can still sometimes involve sudden floods of data to targeted spots, she noted. For instance, in a social network, a famous person may swiftly gain followers after some newsworthy event.

“It’s my belief that the algorithm will lead to performance advantages in real-world situations,” Bender said. However, the researchers cautioned, as with any theoretical advance, making the new algorithm into something that performs well in practice will require serious work.

The recent improvements, Blelloch predicted, are likely to draw more researchers to the bookshelf problem, with a view not just to practical implementations, but also to further theoretical advances. The burning question now is, can researchers get all the way to log*n*?

If they can—in a way that can be implemented in the real world—then bookshelf algorithms might offer serious competition to binary search trees, which are currently the most widely used data structure for sorted data. Then, Kuszmaul said, “You would actually have a data structure that would change the world.”

There are, he warned, “a bunch of seemingly impossible hurdles between here and there.”

Then again, the new work “opens things up,” Blelloch said. “Who knows what’s the best we can do? Maybe we can get to log*n*.”

## Further Reading

- *Bender, M. et al.*  
	**Anti-persistence on persistent storage: History-independent sparse tables and dictionaries. In *Proc. 35th ACM SIGMOD-SIGACT-SIGART Symposium on Principles of Database Systems (PODS)*, pages 289-302, June 2016.**
- *Bender, M. et al.*  
	**Online list labeling: breaking the log2n barrier. *IEEE 63rd Annual Symposium on Foundations of Computer Science (FOCS)*, pages 980-990, 2022.**
-   Bulánek, J. et al.  
	**Tight lower bounds for the online labeling problem. In *Proc. 44th annual ACM Symposium on Theory of Computing (STOC)*, pages 1185-1198, 2012.**
- *Bulánek, J. et al.*  
	**On randomized online labeling with polynomially many labels. In *Proc. International Colloquium on Autamata, Languages, and Programming (ICALP), volume 7965 of Lecture Notes in Computer Science*, pages 291-203, Springer, 2013.**
- *Dietz, P. and Zhang, J.*  
	**Lower bounds for monotonic list labeling. In *Scandinavian Workshop on Algorithm Theory, volume 447 of Lecture Notes in Computer Science*, pages 173-180, Springer, 1990.**
- *Dietz, P. et al.*  
	**A tight lower bound for online monotonic list labeling. *SIAM Journal on Discrete Mathematics, 18* (3):626-637, 2004.**
- *Itai, A. et al.*  
	**“A sparse table implementation of priority queues.” In *Proc. 8th International Colloquium on Automata, Languages and Programming (ICALP), volume 115 of Lecture Notes in Computer Science*, pages 417-431, Springer, 1981.**