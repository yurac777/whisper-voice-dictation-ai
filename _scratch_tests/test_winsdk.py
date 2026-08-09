import asyncio
from winsdk.windows.media.control import GlobalSystemMediaTransportControlsSessionManager, GlobalSystemMediaTransportControlsSessionPlaybackStatus

async def get_media_status():
    manager = await GlobalSystemMediaTransportControlsSessionManager.request_async()
    session = manager.get_current_session()
    if session:
        info = session.get_playback_info()
        return info.playback_status == GlobalSystemMediaTransportControlsSessionPlaybackStatus.PLAYING
    return False

print(asyncio.run(get_media_status()))
