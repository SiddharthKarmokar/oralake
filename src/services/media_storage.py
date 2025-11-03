"""
Media Storage Module for OraLake
Handles image and video storage with version control
"""

from src import logger
from src.services.oralake import add_object, get_object, update_object, rollback_object
from typing import Optional, Tuple, Dict
from pathlib import Path
import io
from PIL import Image
import json
from datetime import datetime
import time


class MediaStorage:
    """Handle image and video storage with metadata and version control"""
    
    SUPPORTED_IMAGE_FORMATS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp', '.tiff'}
    SUPPORTED_VIDEO_FORMATS = {'.mp4', '.avi', '.mov', '.mkv', '.webm', '.flv'}
    
    @staticmethod
    def save_image(
        file_path: str,
        name: Optional[str] = None,
        tags: str = "image",
        description: Optional[str] = None,
        compress: bool = True,
        quality: int = 85,
        max_dimension: Optional[int] = None
    ) -> int:
        start_time = time.time()
        path = Path(file_path)
        
        if path.suffix.lower() not in MediaStorage.SUPPORTED_IMAGE_FORMATS:
            raise ValueError(f"Unsupported image format: {path.suffix}")
        
        name = name or path.stem
        
        with Image.open(file_path) as img:
            format_name = img.format
            original_size = img.size
            mode = img.mode
            
            if max_dimension and max(img.size) > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                logger.info(f"Resized image from {original_size} to {img.size}")
            
            if compress and img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            buffer = io.BytesIO()
            save_format = 'JPEG' if compress else format_name
            save_kwargs = {'quality': quality, 'optimize': True} if compress else {}
            
            img.save(buffer, format=save_format, **save_kwargs)
            image_bytes = buffer.getvalue()
        
        schema_hint = json.dumps({
            'media_type': 'image',
            'format': format_name,
            'original_size': original_size,
            'current_size': list(img.size),
            'mode': mode,
            'compressed': compress,
            'quality': quality if compress else None,
            'file_size_bytes': len(image_bytes),
            'timestamp': datetime.now().isoformat()
        })
        
        object_id = add_object(
            name=name,
            obj_type='IMAGE',
            content=image_bytes,
            tags=tags,
            description=description or f"Image: {name}",
            schema_hint=schema_hint
        )

        elapsed = (time.time() - start_time) * 1000
        logger.info(f"Saved image '{name}' with ID {object_id} ({len(image_bytes)} bytes) in {elapsed:.2f} ms")
        return object_id
    
    @staticmethod
    def save_video(
        file_path: str,
        name: Optional[str] = None,
        tags: str = "video",
        description: Optional[str] = None,
        chunk_size: int = 10 * 1024 * 1024
    ) -> int:
        start_time = time.time()
        path = Path(file_path)
        
        if path.suffix.lower() not in MediaStorage.SUPPORTED_VIDEO_FORMATS:
            raise ValueError(f"Unsupported video format: {path.suffix}")
        
        name = name or path.stem
        
        with open(file_path, 'rb') as f:
            video_bytes = f.read()
        
        schema_hint = json.dumps({
            'media_type': 'video',
            'format': path.suffix.lower()[1:],
            'file_size_bytes': len(video_bytes),
            'timestamp': datetime.now().isoformat(),
            'original_filename': path.name
        })
        
        object_id = add_object(
            name=name,
            obj_type='VIDEO',
            content=video_bytes,
            tags=tags,
            description=description or f"Video: {name}",
            schema_hint=schema_hint
        )
        
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"Saved video '{name}' with ID {object_id} ({len(video_bytes)} bytes) in {elapsed:.2f} ms")
        return object_id
    
    @staticmethod
    def get_image(object_id: int, save_to: Optional[str] = None) -> Tuple[bytes, Dict]:
        start_time = time.time()
        image_bytes = get_object(object_id)
        
        if image_bytes is None:
            raise ValueError(f"Image with ID {object_id} not found")
        
        img = Image.open(io.BytesIO(image_bytes))
        metadata = {
            'format': img.format,
            'size': img.size,
            'mode': img.mode,
            'file_size_bytes': len(image_bytes)
        }
        
        if save_to:
            with open(save_to, 'wb') as f:
                f.write(image_bytes)
            logger.info(f"Saved image to {save_to}")
        
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"Retrieved image ID {object_id} in {elapsed:.2f} ms")
        return image_bytes, metadata
    
    @staticmethod
    def get_video(object_id: int, save_to: Optional[str] = None) -> Tuple[bytes, Dict]:
        start_time = time.time()
        video_bytes = get_object(object_id)
        
        if video_bytes is None:
            raise ValueError(f"Video with ID {object_id} not found")
        
        metadata = {'file_size_bytes': len(video_bytes)}
        
        if save_to:
            with open(save_to, 'wb') as f:
                f.write(video_bytes)
            logger.info(f"Saved video to {save_to}")
        
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"Retrieved video ID {object_id} in {elapsed:.2f} ms")
        return video_bytes, metadata
    
    @staticmethod
    def update_image(
        name: str,
        file_path: str,
        tags: str = "image",
        description: Optional[str] = None,
        compress: bool = True,
        quality: int = 85,
        max_dimension: Optional[int] = None
    ) -> bool:
        start_time = time.time()
        path = Path(file_path)
        
        with Image.open(file_path) as img:
            format_name = img.format
            original_size = img.size
            mode = img.mode
            
            if max_dimension and max(img.size) > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
            
            if compress and img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            buffer = io.BytesIO()
            save_format = 'JPEG' if compress else format_name
            save_kwargs = {'quality': quality, 'optimize': True} if compress else {}
            img.save(buffer, format=save_format, **save_kwargs)
            image_bytes = buffer.getvalue()
        
        result = update_object(
            name=name,
            obj_type='IMAGE',
            content=image_bytes,
            tags=tags,
            description=description or f"Updated image: {name}"
        )
        
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"Updated image '{name}' ({len(image_bytes)} bytes) in {elapsed:.2f} ms")
        return result
    
    @staticmethod
    def update_video(
        name: str,
        file_path: str,
        tags: str = "video",
        description: Optional[str] = None
    ) -> bool:
        start_time = time.time()
        path = Path(file_path)
        
        with open(file_path, 'rb') as f:
            video_bytes = f.read()
        
        result = update_object(
            name=name,
            obj_type='VIDEO',
            content=video_bytes,
            tags=tags,
            description=description or f"Updated video: {name}"
        )
        
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"Updated video '{name}' ({len(video_bytes)} bytes) in {elapsed:.2f} ms")
        return result
    
    @staticmethod
    def rollback_media(name: str, media_type: str, version: int, save_to: Optional[str] = None) -> bool:
        start_time = time.time()
        if media_type.upper() not in ['IMAGE', 'VIDEO']:
            raise ValueError("media_type must be 'IMAGE' or 'VIDEO'")
        
        result = rollback_object(name, media_type.upper(), version)
        elapsed = (time.time() - start_time) * 1000
        
        if result:
            logger.info(f"Rolled back {media_type} '{name}' to version {version} in {elapsed:.2f} ms")
        else:
            logger.warning(f"Rollback failed for {media_type} '{name}' (version {version}) after {elapsed:.2f} ms")
        
        return result


def save_image_from_bytes(
    image_bytes: bytes,
    name: str,
    tags: str = "image",
    description: Optional[str] = None
) -> int:
    start_time = time.time()
    object_id = add_object(
        name=name,
        obj_type='IMAGE',
        content=image_bytes,
        tags=tags,
        description=description
    )
    elapsed = (time.time() - start_time) * 1000
    logger.info(f"Saved image '{name}' from bytes (ID {object_id}) in {elapsed:.2f} ms")
    return object_id


def convert_image_format(
    object_id: int,
    output_format: str = 'JPEG',
    quality: int = 85
) -> bytes:
    start_time = time.time()
    image_bytes = get_object(object_id)
    
    if image_bytes is None:
        raise ValueError(f"Image with ID {object_id} not found")
    
    with Image.open(io.BytesIO(image_bytes)) as img:
        buffer = io.BytesIO()
        if output_format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        save_kwargs = {'quality': quality} if output_format.upper() in ['JPEG', 'WEBP'] else {}
        img.save(buffer, format=output_format.upper(), **save_kwargs)
        converted = buffer.getvalue()
    
    elapsed = (time.time() - start_time) * 1000
    logger.info(f"Converted image ID {object_id} to {output_format.upper()} in {elapsed:.2f} ms")
    return converted


def create_thumbnail(
    object_id: int,
    size: Tuple[int, int] = (150, 150),
    save_as_new: bool = True,
    thumbnail_name: Optional[str] = None
) -> int:
    start_time = time.time()
    image_bytes = get_object(object_id)
    
    if image_bytes is None:
        raise ValueError(f"Image with ID {object_id} not found")
    
    with Image.open(io.BytesIO(image_bytes)) as img:
        img.thumbnail(size, Image.Resampling.LANCZOS)
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG', quality=85, optimize=True)
        thumbnail_bytes = buffer.getvalue()
    
    if save_as_new:
        name = thumbnail_name or f"thumbnail_{object_id}"
        new_id = add_object(
            name=name,
            obj_type='IMAGE',
            content=thumbnail_bytes,
            tags='thumbnail,image',
            description=f"Thumbnail of image ID {object_id}"
        )
        elapsed = (time.time() - start_time) * 1000
        logger.info(f"Created thumbnail '{name}' (ID {new_id}) in {elapsed:.2f} ms")
        return new_id
    
    elapsed = (time.time() - start_time) * 1000
    logger.info(f"Generated thumbnail for image ID {object_id} in {elapsed:.2f} ms")
    return thumbnail_bytes
