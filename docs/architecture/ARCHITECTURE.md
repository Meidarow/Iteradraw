This document decribes the architecture and intention behind the design of Iteradraw.

## Iteradraw
### Big picture
The main intention with Iteradraw is ultimately to provide an essential artist compation app,
that allows users to hold gesture drawing/slideshow sessions for iterative practice,
alongside a streak/study-tracking framework.

The primary window allows the user to configure and start slideshow sessions.
In this page, the user can define groups of folders and select folders to be used as
sources for images for the slideshow. Aditionally the user can select a singular 
timer to be used for all slides, or define a number os timers to be run sequentially 
in a "pre-defined session". Ultimately the user may choose between a sorted indexing
of the images or randomize the sequence --- in interface: "shuffle" --- and begin 
the session.

### Behind the scenes: Defining speedy UX

This app has two core pillars to its philosophy:
1) Low resource footprint: The user of the app is expected to draw alongside 
the slideshow, and considering that a large cohort of users is likely to prefer
digital art, we must run a tight ship. Art apps are known to be resource hungry; we don't want to step on their toes.
2) Fast: Simple, but the more important of the pillars. People want their 
images to show up immediatelly, not after 4 seconds. We intend to offer massive 
perceived speed, a clean and smooth UX and a responsive-at-all-times UI.

In terms of metrics, these can be summed up as:
* Total RAM/VRAM footprint: <50MB;
* Only GUI thread on high priority;
* Image load time: <100ms;

As the user selects folders a dedicated service verifies whether these folders must 
be crawled again and enqueuing them in the crawler coordinator's queue.

# "Top Change" Shuffle

To ensure instant starts to slideshows even with a shuffled order, where
the first images may not be preloaded into thumbnails, we perform a top change,
wherein we introduce a random preloaded image onto the top of the index.