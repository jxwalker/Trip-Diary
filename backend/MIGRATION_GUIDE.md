# Migration Guide: Legacy to Modular Architecture

## 🎯 **Overview**

This guide helps you migrate from the legacy monolithic structure to the new modular architecture. The migration can be done incrementally without breaking existing functionality.

## 📋 **Migration Checklist**

### ✅ **Completed**
- [x] Modular API structure (routes separated)
- [x] Models organization (API, Domain, Database)
- [x] Configuration system (environment-aware)
- [x] Error handling (custom exceptions)
- [x] Testing infrastructure (utilities and fixtures)
- [x] Service interfaces (base classes)

### 🔄 **In Progress**
- [ ] Service layer migration
- [ ] Database layer updates
- [ ] Middleware enhancements
- [ ] Documentation updates

### 📅 **Planned**
- [ ] Performance optimizations
- [ ] Security enhancements
- [ ] Monitoring integration
- [ ] CI/CD pipeline updates

## 🔧 **Step-by-Step Migration**

### **Step 1: Update Configuration Usage**

**Before (Legacy):**
```python
from config import config

host = config.HOST
port = config.PORT
api_key = config.OPENAI_API_KEY
```

**After (New):**
```python
from src.config import get_settings

settings = get_settings()
host = settings.api.host
port = settings.api.port
api_key = settings.services.openai_api_key
```

### **Step 2: Update Model Imports**

**Before (Legacy):**
```python
from src.models.user_profile import UserProfile
from src.services.database_service import TripData
```

**After (New):**
```python
from src.models import UserProfile, TripData
# or specifically:
from src.models.domain_models import UserProfile
from src.models.database_models import TripData
```

### **Step 3: Update Error Handling**

**Before (Legacy):**
```python
from fastapi import HTTPException

if not trip_data:
    raise HTTPException(status_code=404, detail="Trip not found")
```

**After (New):**
```python
from src.core.exceptions import NotFoundError

if not trip_data:
    raise NotFoundError(
        message="Trip not found",
        resource_type="trip",
        resource_id=trip_id
    )
```

### **Step 4: Update Service Usage**

**Before (Legacy):**
```python
from src.services.llm_extractor import LLMExtractor

extractor = LLMExtractor()
result = await extractor.extract_travel_info(text)
```

**After (New):**
```python
from src.services.interfaces.base import service_registry

llm_service = service_registry.get("llm_extractor")
result = await llm_service.extract_travel_info(text)
```

### **Step 5: Update Route Definitions**

**Before (Legacy):**
```python
# In main.py
@app.post("/api/upload")
async def upload_files(...):
    # route logic here
```

**After (New):**
```python
# In src/api/routes/upload.py
from fastapi import APIRouter

router = APIRouter(prefix="/api", tags=["upload"])

@router.post("/upload")
async def upload_files(...):
    # route logic here
```

## 🔄 **Service Migration Pattern**

### **1. Create Service Interface**
```python
# src/services/interfaces/my_service.py
from abc import ABC, abstractmethod
from .base import BaseService

class MyServiceInterface(BaseService):
    @abstractmethod
    async def process_data(self, data: Any) -> Any:
        pass
```

### **2. Update Existing Service**
```python
# src/services/my_service.py
from .interfaces.my_service import MyServiceInterface

class MyService(MyServiceInterface):
    async def initialize(self):
        # initialization logic
        pass
    
    async def health_check(self):
        return {"status": "healthy"}
    
    async def cleanup(self):
        # cleanup logic
        pass
    
    async def process_data(self, data: Any) -> Any:
        # existing logic
        pass
```

### **3. Register Service**
```python
# src/api/app_factory.py or dependency injection
from src.services.interfaces.base import service_registry
from src.services.my_service import MyService

service_registry.register("my_service", MyService())
```

## 📝 **Configuration Migration**

### **Environment Files**

Create environment-specific configuration files:

**.env.development**
```bash
ENVIRONMENT=development
DEBUG=true
API_HOST=localhost
API_PORT=8000
LOG_LEVEL=DEBUG
```

**.env.production**
```bash
ENVIRONMENT=production
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO
```

### **Update Config Usage**
```python
# Old way
from config import config
if config.ENVIRONMENT == "development":
    # development logic

# New way
from src.config import get_settings
settings = get_settings()
if settings.is_development:
    # development logic
```

## 🧪 **Testing Migration**

### **Update Test Imports**
```python
# Old way
from tests.fixtures import sample_data

# New way
from tests.utils import create_sample_trip_data
from tests.fixtures import sample_trip
```

### **Use New Test Utilities**
```python
# Old way
def test_upload():
    # manual file creation
    with open("test.pdf", "w") as f:
        f.write("test content")
    # test logic
    os.remove("test.pdf")

# New way
def test_upload(file_manager):
    test_file = file_manager.create_test_pdf("test content")
    # test logic
    # automatic cleanup
```

## 🚨 **Breaking Changes**

### **Import Paths**
- `from config import config` → `from src.config import get_settings`
- `from src.models.user_profile import UserProfile` → `from src.models import UserProfile`
- Direct service imports → Service registry usage

### **Configuration Access**
- `config.HOST` → `settings.api.host`
- `config.OPENAI_API_KEY` → `settings.services.openai_api_key`
- `config.ENVIRONMENT` → `settings.environment`

### **Error Handling**
- `HTTPException` → Custom exceptions from `src.core.exceptions`
- Manual error responses → Standardized error responses

## 🔧 **Compatibility Layer**

To ease migration, you can create a compatibility layer:

```python
# src/compat.py
"""Compatibility layer for legacy code"""
from src.config import get_settings

# Legacy config object
class LegacyConfig:
    def __init__(self):
        self._settings = get_settings()
    
    @property
    def HOST(self):
        return self._settings.api.host
    
    @property
    def PORT(self):
        return self._settings.api.port
    
    @property
    def OPENAI_API_KEY(self):
        return self._settings.services.openai_api_key

# Create legacy config instance
config = LegacyConfig()
```

## 📊 **Migration Progress Tracking**

### **Phase 1: Foundation (Completed)**
- ✅ Modular API structure
- ✅ Models organization
- ✅ Configuration system
- ✅ Error handling
- ✅ Testing infrastructure

### **Phase 2: Service Layer (In Progress)**
- 🔄 Service interfaces
- 🔄 Service registry
- 🔄 Dependency injection
- ⏳ Legacy service migration

### **Phase 3: Enhancement (Planned)**
- ⏳ Performance optimizations
- ⏳ Security enhancements
- ⏳ Monitoring integration
- ⏳ Documentation completion

## 🎯 **Next Actions**

### **Immediate (This Week)**
1. Update existing services to use new interfaces
2. Migrate remaining routes to modular structure
3. Update tests to use new utilities
4. Create service registry configuration

### **Short Term (Next 2 Weeks)**
1. Complete service layer migration
2. Update all configuration usage
3. Implement comprehensive error handling
4. Add monitoring and health checks

### **Long Term (Next Month)**
1. Performance optimization
2. Security enhancements
3. Complete documentation
4. CI/CD pipeline updates

## 🆘 **Troubleshooting**

### **Common Issues**

**Import Errors:**
```bash
ModuleNotFoundError: No module named 'src.config'
```
**Solution:** Ensure `src` directory is in Python path or use relative imports.

**Configuration Errors:**
```bash
AttributeError: 'Settings' object has no attribute 'HOST'
```
**Solution:** Update to new configuration structure: `settings.api.host`

**Service Not Found:**
```bash
KeyError: 'llm_service'
```
**Solution:** Ensure service is registered in service registry.

### **Getting Help**

1. Check the `ARCHITECTURE.md` for detailed structure
2. Review test files for usage examples
3. Check existing migrated routes for patterns
4. Use the compatibility layer for gradual migration

## ✅ **Validation**

After migration, verify:
- [ ] All tests pass
- [ ] API endpoints respond correctly
- [ ] Configuration loads properly
- [ ] Services initialize successfully
- [ ] Error handling works as expected
- [ ] Logging functions correctly
