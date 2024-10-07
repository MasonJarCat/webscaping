"""
Pydantic Model to store dataframe data and metadata
"""

import pandas as pd
from pydantic import BaseModel, field_validator
from typing import List, Dict, Any, Optional, Union
import numpy as np


class DataFrameOutput(BaseModel):
    """A Pydantic Class for handling transmission of Pandas DataFrame data from the server to the client"""

    data: List[Dict[Any, Any]]
    description: Optional[Union[str, Dict[str, Any]]] = None

    @field_validator("description", mode="before")
    def format_descr(cls, v):
        """makes sure that the description attribute is a dict"""
        if isinstance(v, str):
            return {"description": v}
        else:
            return v

    @field_validator("data", mode="before")
    def convert_df_to_dict_list(cls, v):
        """Numpy arrays are not json serializeable out of the box"""
        if isinstance(v, pd.DataFrame):
            for col in v.columns:
                if isinstance(v[col].dtype, np.ndarray):
                    v[col] = v[col].apply(lambda x: [i for i in x])
            v = v.to_dict(orient="records")
        return v

    @property
    def dataframe(self):
        """Converts data back into a pandas DataFrame whenever called. So you can grab this value, manipulate, and make a new DFoutput to return in you FastAPI app."""
        return pd.DataFrame(self.data)
