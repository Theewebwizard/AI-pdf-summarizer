import aiofiles
import uuid

async def save_file_temp(file) -> str:
    filename = f"temp_{uuid.uuid4()}.pdf"
    filepath = f"/tmp/{filename}"
    async with aiofiles.open(filepath, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    return filepath
