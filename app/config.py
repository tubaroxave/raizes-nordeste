import os
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./raizes.db")
JWT_SECRET = os.getenv("JWT_SECRET", "esse_segredo_eh_muito_bom_mesmo_ein_nossa")
ACCESS_TOKEN_MINUTES = 60
