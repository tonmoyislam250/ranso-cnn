import joblib, os
import pandas as pd
import numpy as np
import itertools
from sklearn.pipeline import Pipeline


def createDataframeFromPEdump(pe):
    dosHeaders = [
        "e_magic",
        "e_cblp",
        "e_cp",
        "e_crlc",
        "e_cparhdr",
        "e_minalloc",
        "e_maxalloc",
        "e_ss",
        "e_sp",
        "e_csum",
        "e_ip",
        "e_cs",
        "e_lfarlc",
        "e_ovno",
        "e_oemid",
        "e_oeminfo",
        "e_lfanew",
    ]
    fileHeaders = [
        "Machine",
        "NumberOfSections",
        "TimeDateStamp",
        "PointerToSymbolTable",
        "NumberOfSymbols",
        "SizeOfOptionalHeader",
        "Characteristics",
    ]
    optionalHeaders = [
        "Magic",
        "MajorLinkerVersion",
        "MinorLinkerVersion",
        "SizeOfCode",
        "SizeOfInitializedData",
        "SizeOfUninitializedData",
        "AddressOfEntryPoint",
        "BaseOfCode",
        "ImageBase",
        "SectionAlignment",
        "FileAlignment",
        "MajorOperatingSystemVersion",
        "MinorOperatingSystemVersion",
        "MajorImageVersion",
        "MinorImageVersion",
        "MajorSubsystemVersion",
        "MinorSubsystemVersion",
        "SizeOfHeaders",
        "CheckSum",
        "SizeOfImage",
        "Subsystem",
        "DllCharacteristics",
        "SizeOfStackReserve",
        "SizeOfStackCommit",
        "SizeOfHeapReserve",
        "SizeOfHeapCommit",
        "LoaderFlags",
        "NumberOfRvaAndSizes",
    ]
    imageDirectory = [
        "ImageDirectoryEntryExport",
        "ImageDirectoryEntryImport",
        "ImageDirectoryEntryResource",
        "ImageDirectoryEntryException",
        "ImageDirectoryEntrySecurity",
    ]

    dheaders = {}
    fheaders = {}
    oheaders = {}
    imd1 = {}

    for x in dosHeaders:
        dheaders[x] = getattr(pe.DOS_HEADER, x)
    df = pd.DataFrame(dheaders, index=[0])

    for i in fileHeaders:
        fheaders[i] = getattr(pe.FILE_HEADER, i)
    df = pd.concat([df, (pd.DataFrame(fheaders, index=[0]))], axis=1)

    for y in optionalHeaders:
        oheaders[y] = getattr(pe.OPTIONAL_HEADER, y)
    df = pd.concat([df, (pd.DataFrame(oheaders, index=[0]))], axis=1)

    for q in pe.OPTIONAL_HEADER.DATA_DIRECTORY:
        imd1[q.name] = q.VirtualAddress
    imd1 = dict(itertools.islice(imd1.items(), 5))
    df = pd.concat([df, (pd.DataFrame(imd1, index=[0]))], axis=1)

    return df


def getPredictions(df):
    workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scaler_pkl_path = os.path.join(workspace_dir, "components", "SScaler.pkl")
    pca_pkl_path = os.path.join(workspace_dir, "components", "PCA.pkl")
    model_pkl_path = os.path.join(workspace_dir, "components", "model.pkl")
    load_scaler = joblib.load(open(scaler_pkl_path, "rb"))
    load_skpca = joblib.load(open(pca_pkl_path, "rb"))
    load_model = joblib.load(open(model_pkl_path, "rb"))
    pipe = Pipeline([("scale", load_scaler), ("pca", load_skpca), ("clf", load_model)])
    df = np.array(df)
    df = df.reshape(1, -1)
    results = pipe.predict_proba(df)

    return results[0]
