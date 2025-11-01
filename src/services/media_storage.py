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
        """
        Save an image to OraLake with optional compression and resizing
        
        Args:
            file_path: Path to the image file
            name: Custom name (defaults to filename)
            tags: Comma-separated tags
            compress: Whether to compress the image
            quality: JPEG quality (1-100)
            max_dimension: Maximum width or height (maintains aspect ratio)
            
        Returns:
            object_id of the saved image
        """
        path = Path(file_path)
        
        if path.suffix.lower() not in MediaStorage.SUPPORTED_IMAGE_FORMATS:
            raise ValueError(f"Unsupported image format: {path.suffix}")
        
        name = name or path.stem
        
        # Read and process image
        with Image.open(file_path) as img:
            # Get original metadata
            format_name = img.format
            original_size = img.size
            mode = img.mode
            
            # Resize if needed
            if max_dimension and max(img.size) > max_dimension:
                img.thumbnail((max_dimension, max_dimension), Image.Resampling.LANCZOS)
                logger.info(f"Resized image from {original_size} to {img.size}")
            
            # Convert to RGB if necessary (for JPEG)
            if compress and img.mode in ('RGBA', 'LA', 'P'):
                rgb_img = Image.new('RGB', img.size, (255, 255, 255))
                rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                img = rgb_img
            
            # Save to bytes
            buffer = io.BytesIO()
            save_format = 'JPEG' if compress else format_name
            save_kwargs = {'quality': quality, 'optimize': True} if compress else {}
            
            img.save(buffer, format=save_format, **save_kwargs)
            image_bytes = buffer.getvalue()
        
        # Create metadata schema
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
        
        # Save to database
        object_id = add_object(
            name=name,
            obj_type='IMAGE',
            content=image_bytes,
            tags=tags,
            description=description or f"Image: {name}",
            schema_hint=schema_hint
        )
        
        logger.info(f"Saved image '{name}' with ID {object_id} ({len(image_bytes)} bytes)")
        return object_id
    
    @staticmethod
    def save_video(
        file_path: str,
        name: Optional[str] = None,
        tags: str = "video",
        description: Optional[str] = None,
        chunk_size: int = 10 * 1024 * 1024  # 10MB chunks for large videos
    ) -> int:
        """
        Save a video to OraLake
        
        Args:
            file_path: Path to the video file
            name: Custom name (defaults to filename)
            tags: Comma-separated tags
            description: Video description
            chunk_size: Not used yet, but reserved for future chunking implementation
            
        Returns:
            object_id of the saved video
        """
        path = Path(file_path)
        
        if path.suffix.lower() not in MediaStorage.SUPPORTED_VIDEO_FORMATS:
            raise ValueError(f"Unsupported video format: {path.suffix}")
        
        name = name or path.stem
        
        # Read video file
        with open(file_path, 'rb') as f:
            video_bytes = f.read()
        
        # Create metadata schema
        schema_hint = json.dumps({
            'media_type': 'video',
            'format': path.suffix.lower()[1:],  # Remove the dot
            'file_size_bytes': len(video_bytes),
            'timestamp': datetime.now().isoformat(),
            'original_filename': path.name
        })
        
        # Save to database
        object_id = add_object(
            name=name,
            obj_type='VIDEO',
            content=video_bytes,
            tags=tags,
            description=description or f"Video: {name}",
            schema_hint=schema_hint
        )
        
        logger.info(f"Saved video '{name}' with ID {object_id} ({len(video_bytes)} bytes)")
        return object_id
    
    @staticmethod
    def get_image(object_id: int, save_to: Optional[str] = None) -> Tuple[bytes, Dict]:
        """
        Retrieve an image from OraLake
        
        Args:
            object_id: ID of the image object
            save_to: Optional path to save the image file
            
        Returns:
            Tuple of (image_bytes, metadata_dict)
        """
        image_bytes = get_object(object_id)
        
        if image_bytes is None:
            raise ValueError(f"Image with ID {object_id} not found")
        
        # Parse image to get metadata
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
        
        return image_bytes, metadata
    
    @staticmethod
    def get_video(object_id: int, save_to: Optional[str] = None) -> Tuple[bytes, Dict]:
        """
        Retrieve a video from OraLake
        
        Args:
            object_id: ID of the video object
            save_to: Optional path to save the video file
            
        Returns:
            Tuple of (video_bytes, metadata_dict)
        """
        video_bytes = get_object(object_id)
        
        if video_bytes is None:
            raise ValueError(f"Video with ID {object_id} not found")
        
        metadata = {
            'file_size_bytes': len(video_bytes)
        }
        
        if save_to:
            with open(save_to, 'wb') as f:
                f.write(video_bytes)
            logger.info(f"Saved video to {save_to}")
        
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
        """
        Update an existing image (creates a new version)
        
        Args:
            name: Name of the existing image object
            file_path: Path to the new image file
            tags: Updated tags
            description: Updated description
            compress: Whether to compress the image
            quality: JPEG quality (1-100)
            max_dimension: Maximum width or height
            
        Returns:
            True if successful
        """
        path = Path(file_path)
        
        # Read and process image (same as save_image)
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
        
        # Update in database
        result = update_object(
            name=name,
            obj_type='IMAGE',
            content=image_bytes,
            tags=tags,
            description=description or f"Updated image: {name}"
        )
        
        logger.info(f"Updated image '{name}' ({len(image_bytes)} bytes)")
        return result
    
    @staticmethod
    def update_video(
        name: str,
        file_path: str,
        tags: str = "video",
        description: Optional[str] = None
    ) -> bool:
        """
        Update an existing video (creates a new version)
        
        Args:
            name: Name of the existing video object
            file_path: Path to the new video file
            tags: Updated tags
            description: Updated description
            
        Returns:
            True if successful
        """
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
        
        logger.info(f"Updated video '{name}' ({len(video_bytes)} bytes)")
        return result
    
    @staticmethod
    def rollback_media(name: str, media_type: str, version: int, save_to: Optional[str] = None) -> bool:
        """
        Rollback an image or video to a previous version
        
        Args:
            name: Name of the media object
            media_type: 'IMAGE' or 'VIDEO'
            version: Target version number
            save_to: Optional path to save the rolled-back media
            
        Returns:
            True if successful
        """
        if media_type.upper() not in ['IMAGE', 'VIDEO']:
            raise ValueError("media_type must be 'IMAGE' or 'VIDEO'")
        
        result = rollback_object(name, media_type.upper(), version)
        
        if result and save_to:
            # Get the rolled-back content and save it
            # Note: You'd need to get the object_id first
            logger.info(f"Rolled back {media_type} '{name}' to version {version}")
        
        return result


# Utility functions for common operations
def save_image_from_bytes(
    image_bytes: bytes,
    name: str,
    tags: str = "image",
    description: Optional[str] = None
) -> int:
    """
    Save an image directly from bytes (useful for API uploads)
    """
    return add_object(
        name=name,
        obj_type='IMAGE',
        content=image_bytes,
        tags=tags,
        description=description
    )


def convert_image_format(
    object_id: int,
    output_format: str = 'JPEG',
    quality: int = 85
) -> bytes:
    """
    Convert an image to a different format
    
    Args:
        object_id: ID of the source image
        output_format: Target format (JPEG, PNG, WEBP, etc.)
        quality: Quality for lossy formats
        
    Returns:
        Converted image bytes
    """
    image_bytes = get_object(object_id)
    
    if image_bytes is None:
        raise ValueError(f"Image with ID {object_id} not found")
    
    with Image.open(io.BytesIO(image_bytes)) as img:
        buffer = io.BytesIO()
        
        # Convert RGBA to RGB for JPEG
        if output_format.upper() == 'JPEG' and img.mode in ('RGBA', 'LA', 'P'):
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
            img = rgb_img
        
        save_kwargs = {'quality': quality} if output_format.upper() in ['JPEG', 'WEBP'] else {}
        img.save(buffer, format=output_format.upper(), **save_kwargs)
        
        return buffer.getvalue()


def create_thumbnail(
    object_id: int,
    size: Tuple[int, int] = (150, 150),
    save_as_new: bool = True,
    thumbnail_name: Optional[str] = None
) -> int:
    """
    Create a thumbnail from an existing image
    
    Args:
        object_id: ID of the source image
        size: Thumbnail size (width, height)
        save_as_new: If True, saves as new object; if False, returns bytes only
        thumbnail_name: Name for the thumbnail object
        
    Returns:
        object_id of the thumbnail (if save_as_new=True)
    """
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
        return add_object(
            name=name,
            obj_type='IMAGE',
            content=thumbnail_bytes,
            tags='thumbnail,image',
            description=f"Thumbnail of image ID {object_id}"
        )
    
    return thumbnail_bytes