# Copyright 2024 H. Turgut Uyar <uyar@tekir.org>
#
# This file is part of CinemagoerNG.
#
# CinemagoerNG is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# CinemagoerNG is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with CinemagoerNG.  If not, see <http://www.gnu.org/licenses/>.


from abc import ABC, abstractmethod
from typing import (
    Awaitable,
    Callable,
    Generic,
    List,
    Optional,
    TypeVar,
    Union,
)

from . import model, piculet


T = TypeVar("T")

FetchFunction = Callable[..., Union[str, Awaitable[str]]]


class Operation(ABC, Generic[T]):
    """Base class for operations that can be performed sync or async."""

    def __init__(self, fetch_func: FetchFunction):
        self.fetch = fetch_func

    @abstractmethod
    def _process_data_sync(self, data: dict, **kwargs) -> T:
        """Process the scraped data synchronously."""
        pass

    @abstractmethod
    async def _process_data_async(self, data: dict, **kwargs) -> T:
        """Process the scraped data asynchronously."""
        pass

    def _get_url(self, spec: piculet.Spec, **kwargs) -> str:
        """Generate URL from spec and parameters."""
        url_params = {}
        if spec.url_default_params:
            url_params.update(spec.url_default_params)
        url_params.update(kwargs)

        if spec.url_transform:
            return spec.url_transform.apply(
                {"url": spec.url, "params": url_params}
            )
        return spec.url % url_params

    def _scrape_document(self, document: str, spec: piculet.Spec) -> dict:
        """Scrape document using the provided spec."""
        return piculet.scrape(
            document,
            doctype=spec.doctype,
            rules=spec.rules,
            pre=spec.pre,
            post=spec.post,
        )

    def execute(self, spec: piculet.Spec, **kwargs) -> T:
        """Execute the operation synchronously."""

        url = self._get_url(spec, **kwargs)
        document = self.fetch(url, **kwargs)
        data = self._scrape_document(document, spec)
        return self._process_data_sync(data, spec=spec, **kwargs)

    async def execute_async(self, spec: piculet.Spec, **kwargs) -> T:
        """Execute the operation asynchronously."""

        url = self._get_url(spec, **kwargs)
        document = await self.fetch(url, **kwargs)
        data = self._scrape_document(document, spec)
        return await self._process_data_async(data, spec=spec, **kwargs)


class GetTitle(Operation[Optional[model.Title]]):
    """Operation for retrieving a single title."""

    def _process_data_sync(
        self, data: dict, **kwargs
    ) -> Optional[model.Title]:
        if not data:
            return None
        return piculet.deserialize(data, model.Title)

    async def _process_data_async(
        self, data: dict, **kwargs
    ) -> Optional[model.Title]:
        return self._process_data_sync(data, **kwargs)


class UpdateTitle(Operation[None]):
    """Operation for updating a title with additional information."""

    def __init__(
        self, fetch_func: FetchFunction, title: model.Title, keys: List[str]
    ):
        super().__init__(fetch_func)
        self.title = title
        self.keys = keys

    def _update_fields(self, data: dict) -> None:
        """Update title fields from data."""
        for key in self.keys:
            value = data.get(key)
            if value is None:
                continue

            if key == "episodes":
                if isinstance(value, dict):
                    value = piculet.deserialize(value, model.EpisodeMap)
                    self.title.episodes.update(value)
                else:
                    value = piculet.deserialize(value, list[model.TVEpisode])
                    self.title.add_episodes(value)
            elif key == "akas":
                value = [piculet.deserialize(aka, model.AKA) for aka in value]
                self.title.akas.extend(value)
            elif key == "certification":
                value = piculet.deserialize(value, model.Certification)
                setattr(self.title, key, value)
            elif key == "advisories":
                value = piculet.deserialize(value, model.Advisories)
                setattr(self.title, key, value)
            else:
                setattr(self.title, key, value)

    def _process_data_sync(self, data: dict, **kwargs) -> None:
        """Process the data synchronously and handle pagination if needed."""
        self._update_fields(data)

        if kwargs.get("paginate_result") and data.get("has_next_page", False):
            kwargs["after"] = f'"{data["end_cursor"]}"'
            self.execute(**kwargs)

    async def _process_data_async(self, data: dict, **kwargs) -> None:
        """Process the data asynchronously and handle pagination if needed."""
        self._update_fields(data)

        if kwargs.get("paginate_result") and data.get("has_next_page", False):
            kwargs["after"] = f'"{data["end_cursor"]}"'
            await self.execute_async(**kwargs)

