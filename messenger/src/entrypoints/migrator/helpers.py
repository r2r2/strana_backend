from yaml import safe_load

from src.constants import FIXTURES_FOLDER
from src.core.types import LoggerType
from src.modules.storage import models as db_models
from src.modules.storage.helpers import create_engine, create_session
from src.modules.storage.settings import StorageSettings


async def load_fixtures(
    logger: LoggerType,
    settings: StorageSettings,
    load_only: list[str],
) -> None:
    engine, sessionmaker = create_engine(settings.db)

    async with create_session(sessionmaker) as session:
        models_path = FIXTURES_FOLDER / "models"

        allowed_models = None
        if load_only:
            allowed_models = [name.strip().lower() for name in load_only]

        for model_data in models_path.glob("*.yaml"):
            if not model_data.is_file():
                continue

            db_model_name = model_data.stem
            if allowed_models and db_model_name.lower() not in allowed_models:
                continue

            actual_model = getattr(db_models, db_model_name, None)
            if not actual_model:
                raise ValueError(f"Model not found: {db_model_name}")

            with open(model_data, "r", encoding="utf8") as inp:
                model_instances = safe_load(inp)
                for instance in model_instances:
                    instance = actual_model(**instance)
                    session.add(instance)

            logger.debug(f"Created objects for model {db_model_name}")

        await session.commit()

    await engine.dispose()
