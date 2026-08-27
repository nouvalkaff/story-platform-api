from datetime import UTC, datetime
from typing import TypedDict

from sqlalchemy import select

from app.db.session import SessionLocal
from app.models.story import Story, StoryGenre, StoryStatus
from app.models.user import User

ADMIN_EMAIL = "admin@example.com"
REGULAR_USER_EMAIL = "user@example.com"


class StorySeed(TypedDict):
    title: str
    content: str
    status: StoryStatus


class StoryDetails(TypedDict):
    synopsis: str
    genre: StoryGenre
    tags: list[str]


def _story(title: str, content: str, status: StoryStatus) -> StorySeed:
    return {"title": title, "content": content, "status": status}


ADMIN_STORIES = (
    _story(
        "The Lost Kingdom of Ardenia",
        """When cartographer Elian Vey found Ardenia missing from every royal map, he expected an error made by a careless apprentice. Instead, a salt-stained letter arrived beneath his door, bearing the seal of a kingdom erased seventy years earlier. The letter named a lighthouse beyond the northern shoals and warned that its lamp must never go dark. Elian sailed with only a compass inherited from his mother and a disgraced captain who claimed to have seen Ardenia's towers beneath the fog. At the lighthouse they discovered a city held inside a single night, its bells ringing without hands to pull the ropes. To free its people, Elian had to redraw the border that imprisoned them, knowing the new line would also lead the old empire straight to their gates.""",
        StoryStatus.PUBLISHED,
    ),
    _story(
        "Letters from the Glass Observatory",
        """Mira repaired cracked lenses in the mountain observatory, where astronomers listened for messages hidden in starlight. One winter evening, a pattern appeared in the glass: tiny bright strokes spelling the name of her brother, lost at sea six years before. The director ordered silence, fearing the signal would lure treasure hunters up the pass. Mira copied the pattern anyway and followed it through a series of abandoned weather stations. Each lens revealed another memory from her brother's final voyage, not as a ghost story but as instructions for rescuing a crew stranded beyond the ice fields. By dawn she understood that the observatory had never watched the heavens alone; it had been a beacon for people who had nowhere else to send their hope.""",
        StoryStatus.PUBLISHED,
    ),
    _story(
        "The Clockmaker's Last Harbor",
        """At low tide, the harbor of Bellweather exposed a clockwork pier no one remembered building. Tomas, the town's youngest clockmaker, noticed that its brass gears turned only when a ship was about to disappear. His father had vanished that way, leaving behind a pocket watch that ran backward whenever Tomas lied. When a storm drove three fishing boats toward the hidden mechanism, Tomas climbed beneath the pier with the watch in his hand. There he met an old engineer who had kept the harbor alive by stealing minutes from sailors' futures. Tomas refused the bargain and rewound the engine with every honest memory he possessed. The boats returned at sunrise, but the town woke to find that Tomas no longer knew his father's face, only the warmth of a hand guiding his own.""",
        StoryStatus.PUBLISHED,
    ),
    _story(
        "A Map for the Winter Fox",
        """Sera was hired to track a white fox blamed for raiding the grain stores of a valley already buried in snow. The animal left no paw prints, only thin blue lines across frozen windows. Following them, Sera reached an abandoned schoolhouse where children once learned the old language of the mountains. The fox was waiting beside a mural that changed whenever moonlight touched it, revealing paths to sealed granaries beneath the village square. The mayor wanted the creature trapped, but Sera saw that it had been guiding hungry families toward food hidden by a previous council. She chose to expose the hoarding instead. On the first thawing day, the fox crossed the valley one final time, and every window reflected a road leading home.""",
        StoryStatus.PUBLISHED,
    ),
    _story(
        "The Orchard Beyond the Rain",
        """After a season of rain that would not stop, farmer Nalin found a gate growing between two apple trees. Beyond it stood an orchard under clear blue sky, though every branch carried fruit labeled with a person's forgotten wish. Nalin tasted a pear marked with his late wife's name and remembered the small bakery they had planned to open before illness changed everything. Soon neighbors begged him to gather their fruit, but each wish carried a cost: taking it made the ordinary world a little less bearable. Nalin spent weeks listening instead of picking. He taught the village to speak their wishes aloud and build what they could together. When the rain finally ended, the gate had vanished, leaving one new sapling where it stood and a basket of apples meant for no one but the living.""",
        StoryStatus.DRAFT,
    ),
    _story(
        "The Silent Choir of Marrow Bay",
        """Every evening at Marrow Bay, the tide carried a choir's harmony through the empty streets. Lena, a sound archivist fleeing a failed career, came to record it before developers replaced the shore with hotels. Her microphones captured no voices, only the breathing of old houses and the creak of boats tied to docks. An elderly fisherman explained that the town had stopped singing after a shipwreck took half its families, yet the sea remembered every song. Lena traced the melody to a flooded chapel and found hymn books filled with names of people never recovered. She invited the surviving residents to sing into the storm. Their unsteady voices did not banish the sea's choir, but joined it, turning grief from a haunting into a promise that someone would keep listening.""",
        StoryStatus.DRAFT,
    ),
    _story(
        "Embers Under the Library Steps",
        """The city library closed each midnight, but its stone steps stayed warm until dawn. Apprentice historian Oren discovered a furnace beneath them, fed by books that governments had tried to erase. The librarian charged him with protecting the flames without letting them consume the building above. When inspectors arrived to seize a banned diary, Oren was tempted to hide it in the fire forever. Instead, he read it aloud in the public square, where its account of a forgotten strike brought strangers together. The inspectors took the empty cover and declared victory. Beneath the steps, the furnace burned lower but steadier, because the diary no longer depended on paper. Oren understood then that preservation was not a locked room; it was the dangerous work of giving a story more than one witness.""",
        StoryStatus.DRAFT,
    ),
    _story(
        "The River That Remembered Names",
        """Children in Asterford were told never to whisper their names into the river. Mara did it anyway when her younger sister disappeared during the lantern festival, and by morning the current began answering in voices. It spoke the names of missing people from every generation, carrying each one past Mara's doorstep on a ripple of silver. She followed the river upstream through factories, marshes, and an estate where a magistrate had diverted water to hide an old prison. Beneath the estate she found her sister and dozens of descendants of prisoners living in secret rooms. Mara opened the floodgates despite the danger to the town. The river reclaimed its course, and its voices softened. For the first time, the missing were not merely remembered; they were expected at supper.""",
        StoryStatus.DRAFT,
    ),
    _story(
        "The Brass Kite Society",
        """In a city where children learned wind charts before arithmetic, Jun built a brass kite that could fly without string. The Society of Aeronauts confiscated it, insisting such inventions belonged to licensed adults. Jun and her friends broke into the society's rooftop workshop to retrieve it and discovered hundreds of kites pinned like insects, each carrying a message from a neighborhood the council had ignored. Jun's kite rose through a thunderstorm and pulled the messages into the sky where everyone could read them reflected in the clouds. The council promised repairs, though no one trusted promises alone. So the children formed their own society, meeting every Sunday to send kites over broken bridges and dry wells. Years later, pilots still looked for brass wings when they needed to know where help was overdue.""",
        StoryStatus.DRAFT,
    ),
    _story(
        "The House with Seven Doorbells",
        """Rafi inherited a narrow house with seven doorbells and no front door. Each bell rang at a different hour, opening a wall onto a visitor from another possible life: a violinist who never left home, a judge who never forgave his brother, an old man who had chosen money over friendship. Rafi began taking advice from them, until his own days felt crowded with decisions he had not made. On the seventh night, a little girl arrived carrying a bell with no button. She said she was the life he would have if he stopped waiting for certainty. Rafi dismantled the doorbells at dawn, keeping only hers. He opened a real door onto the street and spent the morning calling his brother, buying a violin, and inviting neighbors in for tea.""",
        StoryStatus.DRAFT,
    ),
)

REGULAR_USER_STORIES = (
    _story(
        "Moonlight at the Cedar Station",
        """Niko worked the last shift at Cedar Station, a rural platform scheduled for demolition after the railway adopted faster routes. One night a train without a timetable arrived, its windows glowing with moonlight instead of lamps. A woman stepped out and handed Niko a ticket stamped with tomorrow's date, asking him to deliver a suitcase to the version of herself who had never boarded. The suitcase held letters written by passengers who had chosen courage too late. Niko rode through towns that appeared only while people slept, learning that the train stopped wherever a choice still had time to change. At dawn he returned to Cedar Station, tore up his resignation, and turned the empty waiting room into a place for travelers to leave messages before they became regrets.""",
        StoryStatus.PUBLISHED,
    ),
    _story(
        "The Painter of Borrowed Skies",
        """Iris made a living painting ceilings for wealthy clients who wanted summer above their dining tables. Her finest work hung in a hospital ward, where she painted clouds that moved slowly enough for patients to follow. When a boy named Sol asked for the sky from his village, Iris discovered it had been hidden behind a mining company's smoke. She traveled with Sol's drawings and painted the lost blue across the company's black storage tanks. The murals attracted reporters, then residents, then an investigation. Sol recovered before the hearing, but Iris kept painting there every week. She learned that beauty was not an escape from the world; sometimes it was evidence of what the world had stolen, made too visible to ignore.""",
        StoryStatus.PUBLISHED,
    ),
    _story(
        "Beneath the Copper Bridge",
        """Amina sold tea beneath the Copper Bridge, where commuters hurried past the river and never looked down. One evening she found a small door in the bridge's oldest support, opened by placing a warm cup against the metal. Inside was a workshop run by retired engineers who had spent decades repairing tiny fractures in the city before they became disasters. They invited Amina to join them because her customers told her everything: which stairwell rattled, which street flooded, which landlord ignored a gas smell. Amina organized the gossip into maps. When the bridge cracked during a festival, the engineers knew where to brace it and the crowd had time to leave safely. Her tea stall became a listening post, and the city slowly learned that care often begins with details everyone else calls trivial.""",
        StoryStatus.PUBLISHED,
    ),
    _story(
        "The Sea Between Two Teacups",
        """After their grandmother died, cousins Hana and Dimas inherited two blue teacups that filled with seawater whenever they argued. They had not spoken kindly since a dispute over the family house, so the cups remained dangerously full. One afternoon they found a paper boat floating inside one cup, carrying directions to the island where their grandmother first met their grandfather. They traveled there with the cups wrapped in towels and found a weathered cottage stocked with recipes, photographs, and one final note: love was not agreement, but the willingness to return to the table. Hana and Dimas emptied the cups into the sea together. Back home they kept the house, opening its kitchen every Sunday for neighbors who needed somewhere to settle their own storms.""",
        StoryStatus.PUBLISHED,
    ),
    _story(
        "The Lantern Keeper's Apprentice",
        """Fara wanted to become an engineer, but the only job in her village was assisting the lantern keeper on the cliff. The keeper maintained a row of lamps that guided fishing boats through reefs, each fueled by oil mixed with a memory. Fara hated the ritual until one lamp began flickering with memories that were not hers: a boy lost in a storm, a mother waiting beside an empty bed, a captain afraid to return. She traced the lamp's history and learned the keeper had hidden a wreck because his family owned the negligent shipping company. Fara repaired the light with a public confession, forcing the village to face what it had buried. The boats came home safely that season, and Fara left for engineering school carrying the lantern's lens as proof that truth can be part of any design.""",
        StoryStatus.DRAFT,
    ),
    _story(
        "A Garden Made of Keys",
        """On the edge of the old quarter, Malik tended a garden where keys grew instead of flowers. Every key opened something people had lost the courage to face: a locked attic, a final letter, a workshop abandoned after failure. Malik's own key appeared late one autumn, small and rusted, beneath a rosebush that had never bloomed. It opened the door to his childhood apartment, now occupied by a family who did not recognize him. Inside, he found nothing magical, only the memory of leaving without saying goodbye to his father. Malik used the garden's other keys to help strangers, but kept his own in his pocket until he found his father at a repair shop across town. The conversation was difficult and ordinary, which made it more precious than any secret garden.""",
        StoryStatus.DRAFT,
    ),
    _story(
        "The Last Postcard from Halcyon",
        """Journalist Vera received a postcard each month from Halcyon, a resort island destroyed by a volcanic eruption fifteen years earlier. The cards described cafés, ferry schedules, and rainstorms with such precision that her editor sent her to investigate. She found only black stone and a research camp monitoring new tremors. At night, the radio transmitted the same address printed on the postcards. Vera followed it to a cave where displaced islanders had built a hidden archive of photographs and oral histories, refusing to let outsiders reduce their home to a disaster headline. The postcards were invitations, not ghosts. Vera wrote the story they asked for, naming the people who had rebuilt elsewhere. The next card arrived weeks later from their new community center, with a blank space saved for her reply.""",
        StoryStatus.DRAFT,
    ),
    _story(
        "The Violinist in Apartment 9",
        """When Arman moved into Apartment 8, he heard a violin every night from the empty room next door. The melody changed with the building's troubles: slow when rent increased, sharp when an elevator failed, warm when someone brought home a baby. Curious, Arman asked the landlord, who said Apartment 9 had been vacant for decades. He slipped a note under its door and received one back from a musician who had once organized tenants against eviction. Her letters urged him to speak with his neighbors rather than complain alone. Arman formed a tenants' association, and the building won repairs and fair leases. On the day they celebrated, the violin stopped. In Apartment 9, Arman found a dusty instrument and a lease signed by every resident, past and present.""",
        StoryStatus.DRAFT,
    ),
    _story(
        "Rain on the Red Planet",
        """The first rain forecast for Mars drew settlers from every dome to the observation field. Keiko, a young hydroponics technician, worried that the cloud-seeding plan would ruin the delicate algae farms that supplied oxygen. The colony council dismissed her concerns, calling rain a symbol too valuable to postpone. Keiko sabotaged nothing; instead, she invited the council to spend a night in the greenhouse, where every drop of water had a ledger and a history. Together they redesigned the experiment, directing the storm toward a dormant basin and capturing the runoff in new reservoirs. When rain finally fell, it was brief, red with dust, and unforgettable. Children danced in pressure suits while Keiko watched the gauges rise. She realized that wonder survived scrutiny, and often became safer because someone cared enough to question it.""",
        StoryStatus.DRAFT,
    ),
    _story(
        "The Tailor Who Sewed Sunrises",
        """Old Budi could stitch a sunrise into the lining of any coat, but he used the gift only for people preparing to leave town. A warm glow inside a sleeve helped travelers find their courage before the road did. His granddaughter Lila wanted a sunrise for herself, convinced it would make her brave enough to audition for a conservatory. Budi refused, saying borrowed light fades at the first hard decision. Hurt, Lila entered the audition without it and froze halfway through her song. Then she saw Budi in the back row, wearing a coat sewn with dozens of fading dawns from his own departures. She finished on a whisper that grew into a clear final note. Budi gave her no magic afterward, only a needle, thread, and the patient instruction to make light for others when they needed it.""",
        StoryStatus.DRAFT,
    ),
)


STORY_DETAILS: dict[str, StoryDetails] = {
    "The Lost Kingdom of Ardenia": {
        "synopsis": "A cartographer races to restore a kingdom trapped in a single night before an old empire discovers its hidden border.",
        "genre": StoryGenre.FANTASY,
        "tags": ["lost kingdom", "cartographer", "magic", "adventure"],
    },
    "Letters from the Glass Observatory": {
        "synopsis": "A lens maker deciphers starlight messages that may lead her to a crew lost beyond the ice fields.",
        "genre": StoryGenre.SCI_FI,
        "tags": ["observatory", "stars", "siblings", "rescue"],
    },
    "The Clockmaker's Last Harbor": {
        "synopsis": "A young clockmaker must stop a harbor engine that steals years from sailors to keep ships from vanishing.",
        "genre": StoryGenre.FANTASY,
        "tags": ["clockwork", "harbor", "family", "sacrifice"],
    },
    "A Map for the Winter Fox": {
        "synopsis": "A tracker discovers that a mystical fox is exposing grain hoarding in a snowbound mountain village.",
        "genre": StoryGenre.MYSTERY,
        "tags": ["winter", "fox", "village", "secrets"],
    },
    "The Orchard Beyond the Rain": {
        "synopsis": "A farmer finds an orchard of forgotten wishes and helps his village choose honest hope over easy magic.",
        "genre": StoryGenre.FANTASY,
        "tags": ["orchard", "wishes", "grief", "community"],
    },
    "The Silent Choir of Marrow Bay": {
        "synopsis": "A sound archivist records a town's ghostly sea choir and helps residents transform mourning into song.",
        "genre": StoryGenre.DRAMA,
        "tags": ["coastal town", "music", "loss", "memory"],
    },
    "Embers Under the Library Steps": {
        "synopsis": "An apprentice protects erased histories by bringing a forbidden diary out of hiding and into public memory.",
        "genre": StoryGenre.DRAMA,
        "tags": ["library", "history", "censorship", "truth"],
    },
    "The River That Remembered Names": {
        "synopsis": "A girl follows a river that speaks the names of the missing to uncover a prison hidden beneath an estate.",
        "genre": StoryGenre.MYSTERY,
        "tags": ["river", "missing people", "family", "justice"],
    },
    "The Brass Kite Society": {
        "synopsis": "Children use a forbidden brass kite to broadcast overlooked neighborhoods' needs across the city sky.",
        "genre": StoryGenre.ADVENTURE,
        "tags": ["kites", "children", "city", "activism"],
    },
    "The House with Seven Doorbells": {
        "synopsis": "A man meets versions of his unlived lives through seven doorbells and learns to choose the present.",
        "genre": StoryGenre.FANTASY,
        "tags": ["alternate lives", "home", "family", "choices"],
    },
    "Moonlight at the Cedar Station": {
        "synopsis": "A station attendant boards a midnight train that gives people one final chance to change their choices.",
        "genre": StoryGenre.FANTASY,
        "tags": ["train", "moonlight", "second chances", "travel"],
    },
    "The Painter of Borrowed Skies": {
        "synopsis": "A ceiling painter turns a boy's missing blue sky into a public demand for environmental accountability.",
        "genre": StoryGenre.DRAMA,
        "tags": ["artist", "environment", "hospital", "hope"],
    },
    "Beneath the Copper Bridge": {
        "synopsis": "A tea seller joins retired engineers to map ignored city dangers before a festival bridge disaster.",
        "genre": StoryGenre.DRAMA,
        "tags": ["bridge", "engineers", "community", "city"],
    },
    "The Sea Between Two Teacups": {
        "synopsis": "Feuding cousins follow magical teacups to an island and rediscover their grandmother's lesson about returning.",
        "genre": StoryGenre.ROMANCE,
        "tags": ["family", "teacups", "island", "reconciliation"],
    },
    "The Lantern Keeper's Apprentice": {
        "synopsis": "A lantern keeper's apprentice uncovers a buried shipwreck and makes the village confront its inherited guilt.",
        "genre": StoryGenre.DRAMA,
        "tags": ["lighthouse", "shipwreck", "truth", "engineering"],
    },
    "A Garden Made of Keys": {
        "synopsis": "A gardener whose keys unlock difficult memories must finally use one to speak with his estranged father.",
        "genre": StoryGenre.FANTASY,
        "tags": ["garden", "keys", "father", "forgiveness"],
    },
    "The Last Postcard from Halcyon": {
        "synopsis": "A journalist investigates postcards from a destroyed island and finds a community preserving its own story.",
        "genre": StoryGenre.MYSTERY,
        "tags": ["postcards", "island", "journalist", "survivors"],
    },
    "The Violinist in Apartment 9": {
        "synopsis": "A tenant follows music from a vacant apartment and organizes neighbors to save their homes.",
        "genre": StoryGenre.DRAMA,
        "tags": ["violin", "apartment", "tenants", "community"],
    },
    "Rain on the Red Planet": {
        "synopsis": "A Mars technician challenges a symbolic rain experiment and helps redesign it to protect the colony's oxygen.",
        "genre": StoryGenre.SCI_FI,
        "tags": ["mars", "rain", "colony", "science"],
    },
    "The Tailor Who Sewed Sunrises": {
        "synopsis": "A gifted tailor teaches his granddaughter that lasting courage cannot come from borrowed magic.",
        "genre": StoryGenre.FANTASY,
        "tags": ["tailor", "sunrise", "music", "courage"],
    },
}


def seed_stories() -> None:
    """Insert ten idempotent stories for each standard seed user."""
    with SessionLocal() as session:
        try:
            users = {
                email: session.scalar(select(User).where(User.email == email))
                for email in (ADMIN_EMAIL, REGULAR_USER_EMAIL)
            }
            missing_emails = [email for email, user in users.items() if user is None]
            if missing_emails:
                raise RuntimeError(
                    "Seed users before stories; missing: " + ", ".join(missing_emails)
                )

            for email, stories in (
                (ADMIN_EMAIL, ADMIN_STORIES),
                (REGULAR_USER_EMAIL, REGULAR_USER_STORIES),
            ):
                user = users[email]
                assert user is not None
                for story_data in stories:
                    details = STORY_DETAILS[story_data["title"]]
                    existing_story = session.scalar(
                        select(Story).where(Story.title == story_data["title"])
                    )
                    if existing_story is not None:
                        continue

                    status = story_data["status"]
                    assert isinstance(status, StoryStatus)
                    session.add(
                        Story(
                            title=story_data["title"],
                            content=story_data["content"],
                            synopsis=details["synopsis"],
                            genre=details["genre"],
                            tags=details["tags"],
                            author_id=user.id,
                            status=status,
                            published_at=(
                                datetime.now(UTC)
                                if status is StoryStatus.PUBLISHED
                                else None
                            ),
                        )
                    )

            session.commit()
        except Exception:
            session.rollback()
            raise


if __name__ == "__main__":
    seed_stories()
