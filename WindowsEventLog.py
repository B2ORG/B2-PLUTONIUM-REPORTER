import win32evtlog
import datetime as dt
import xml.etree.ElementTree as XML
from pathlib import Path
from typing import Optional


class WindowsEventLog:
    EVENT_IDS = (1000, 1001, 1002)


    def __init__(self, path_filter: Optional[Path] = None, alltime_events: bool = False, datetime: Optional[dt.datetime] = None):
        self._path_filter = str(path_filter).lower() if path_filter else None
        self._alltime_events = alltime_events
        self._datetime = datetime


    def collect(self) -> list[XML.Element]:
        start_time = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=14)
        iso_time = start_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        eventid_filter = " or ".join(
            f"EventID={eid}" for eid in WindowsEventLog.EVENT_IDS
        )

        time_query = f"and TimeCreated[@SystemTime >= '{iso_time}'"
        if self._alltime_events:
            time_query = ""
        elif self._datetime:
            time_query = f"and TimeCreated[@SystemTime >= '{self._datetime.astimezone(dt.timezone.utc).strftime("%Y-%m-%dT00:00:00.000Z")}' and @SystemTime < '{(self._datetime + dt.timedelta(days=1)).astimezone(dt.timezone.utc).strftime("%Y-%m-%dT00:00:00.000Z")}'"

        query = f"""
        *[System[
            ({eventid_filter})
            {time_query}]
        ]]
        """

        handle = win32evtlog.EvtQuery(
            "Application",
            win32evtlog.EvtQueryReverseDirection,
            query,
        )

        results: list[XML.Element] = []

        while True:
            try:
                events = win32evtlog.EvtNext(handle, 16)
            except Exception:
                break

            if not events:
                break

            for event in events:
                try:
                    raw = win32evtlog.EvtRender(
                        event, win32evtlog.EvtRenderEventXml
                    )
                except Exception:
                    continue

                if self._path_filter and self._path_filter not in raw.lower():
                    continue

                results.append(XML.fromstring(raw))

        return results


    def _extract_attr(self, xml: str, tag: str, attr: str) -> str | None:
        needle = f"<{tag} {attr}=\""
        start = xml.find(needle)
        if start == -1:
            return None
        start += len(needle)
        end = xml.find('"', start)
        return xml[start:end] if end != -1 else None


    def _extract_text(self, xml: str, start_tag: str, end_tag: str) -> str | None:
        start = xml.find(start_tag)
        if start == -1:
            return None
        start += len(start_tag)
        end = xml.find(end_tag, start)
        return xml[start:end] if end != -1 else None
