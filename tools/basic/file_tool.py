"""File operations tool."""
import shutil
from pathlib import Path
import logging
from ..registry import Tool, ToolCategory

logger = logging.getLogger(__name__)


class FileTool:
    """File and directory operations."""
    
    name = "file"
    description = "Perform file and directory operations"
    category = ToolCategory.FILE
    
    @staticmethod
    async def read(path: str, encoding: str = "utf-8") -> dict:
        """Read file contents."""
        logger.info(f"Reading file: {path}")
        
        try:
            file_path = Path(path).expanduser()
            
            if not file_path.exists():
                return {"success": False, "error": f"File not found: {path}"}
            
            with open(file_path, "r", encoding=encoding) as f:
                content = f.read()
            
            return {
                "success": True,
                "content": content,
                "path": str(file_path),
                "size": file_path.stat().st_size
            }
        
        except Exception as e:
            logger.error(f"File read failed: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def write(path: str, content: str, encoding: str = "utf-8") -> dict:
        """Write content to file."""
        logger.info(f"Writing file: {path}")
        
        try:
            file_path = Path(path).expanduser()
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)
            
            return {
                "success": True,
                "path": str(file_path),
                "bytes_written": len(content)
            }
        
        except Exception as e:
            logger.error(f"File write failed: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def delete(path: str, recursive: bool = False) -> dict:
        """Delete a file or directory."""
        logger.info(f"Deleting: {path}")
        
        try:
            file_path = Path(path).expanduser()
            
            if not file_path.exists():
                return {"success": False, "error": f"Path not found: {path}"}
            
            if file_path.is_dir():
                if recursive:
                    shutil.rmtree(file_path)
                else:
                    file_path.rmdir()
            else:
                file_path.unlink()
            
            return {"success": True, "path": str(file_path)}
        
        except Exception as e:
            logger.error(f"File delete failed: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def list_dir(path: str = ".") -> dict:
        """List directory contents."""
        logger.info(f"Listing directory: {path}")
        
        try:
            dir_path = Path(path).expanduser()
            
            if not dir_path.exists():
                return {"success": False, "error": f"Directory not found: {path}"}
            
            if not dir_path.is_dir():
                return {"success": False, "error": f"Not a directory: {path}"}
            
            items = []
            for item in dir_path.iterdir():
                items.append({
                    "name": item.name,
                    "type": "dir" if item.is_dir() else "file",
                    "path": str(item)
                })
            
            return {
                "success": True,
                "path": str(dir_path),
                "items": items
            }
        
        except Exception as e:
            logger.error(f"Directory list failed: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def copy(src: str, dest: str) -> dict:
        """Copy a file or directory."""
        logger.info(f"Copying {src} to {dest}")
        
        try:
            src_path = Path(src).expanduser()
            dest_path = Path(dest).expanduser()
            
            if not src_path.exists():
                return {"success": False, "error": f"Source not found: {src}"}
            
            if src_path.is_dir():
                shutil.copytree(src_path, dest_path)
            else:
                shutil.copy2(src_path, dest_path)
            
            return {"success": True, "src": str(src_path), "dest": str(dest_path)}
        
        except Exception as e:
            logger.error(f"Copy failed: {e}")
            return {"success": False, "error": str(e)}
    
    @staticmethod
    async def move(src: str, dest: str) -> dict:
        """Move a file or directory."""
        logger.info(f"Moving {src} to {dest}")
        
        try:
            src_path = Path(src).expanduser()
            dest_path = Path(dest).expanduser()
            
            if not src_path.exists():
                return {"success": False, "error": f"Source not found: {src}"}
            
            shutil.move(str(src_path), str(dest_path))
            
            return {"success": True, "src": str(src_path), "dest": str(dest_path)}
        
        except Exception as e:
            logger.error(f"Move failed: {e}")
            return {"success": False, "error": str(e)}


def get_file_tools() -> list[Tool]:
    """Get file tool definitions."""
    return [
        Tool(
            name="file_read",
            description="Read file contents. Args: path (str), encoding (str, optional)",
            category=ToolCategory.FILE,
            function=FileTool.read
        ),
        Tool(
            name="file_write",
            description="Write content to file. Args: path (str), content (str)",
            category=ToolCategory.FILE,
            function=FileTool.write
        ),
        Tool(
            name="file_delete",
            description="Delete file or directory. Args: path (str), recursive (bool, optional)",
            category=ToolCategory.FILE,
            function=FileTool.delete
        ),
        Tool(
            name="file_list",
            description="List directory contents. Args: path (str, optional, default '.')",
            category=ToolCategory.FILE,
            function=FileTool.list_dir
        ),
        Tool(
            name="file_copy",
            description="Copy file or directory. Args: src (str), dest (str)",
            category=ToolCategory.FILE,
            function=FileTool.copy
        ),
        Tool(
            name="file_move",
            description="Move file or directory. Args: src (str), dest (str)",
            category=ToolCategory.FILE,
            function=FileTool.move
        ),
    ]
