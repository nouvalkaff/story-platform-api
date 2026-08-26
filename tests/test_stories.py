import asyncio
from datetime import UTC, datetime
from types import SimpleNamespace
from typing import cast
from unittest import TestCase
from unittest.mock import AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.story import StoryStatus
from app.models.user import User
from app.schemas.story import StoryResponse
from app.services.story_service import StoryService


class StoryStatusTests(TestCase):
    def test_story_response_serializes_status(self) -> None:
        story = StoryResponse.model_validate(
            {
                "id": 1,
                "title": "Draft story",
                "content": "Content",
                "status": StoryStatus.DRAFT,
                "author_id": 1,
                "published_at": None,
                "created_by": 1,
                "created_at": datetime.now(UTC),
                "updated_by": 1,
                "updated_at": datetime.now(UTC),
            }
        )

        self.assertEqual(story.status, StoryStatus.DRAFT)

    def test_publish_and_unpublish_set_expected_status_and_timestamp(self) -> None:
        asyncio.run(self._assert_publication_transitions())

    async def _assert_publication_transitions(self) -> None:
        service = StoryService()
        story = SimpleNamespace()
        db = cast(AsyncSession, object())
        current_user = cast(User, SimpleNamespace(id=1))

        with (
            patch.object(
                service,
                "_get_editable_story",
                new=AsyncMock(return_value=story),
            ),
            patch(
                "app.services.story_service.crud_story.set_publication",
                new=AsyncMock(return_value=story),
            ) as set_publication,
        ):
            await service.publish_story(db, 1, current_user=current_user)

            publish_kwargs = set_publication.await_args.kwargs
            self.assertEqual(publish_kwargs["status"], StoryStatus.PUBLISHED)
            self.assertIsInstance(publish_kwargs["published_at"], datetime)
            self.assertEqual(publish_kwargs["published_at"].tzinfo, UTC)

            await service.unpublish_story(db, 1, current_user=current_user)

            unpublish_kwargs = set_publication.await_args.kwargs
            self.assertEqual(unpublish_kwargs["status"], StoryStatus.DRAFT)
            self.assertIsNone(unpublish_kwargs["published_at"])
