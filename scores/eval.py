import os, sys, pickle
import numpy as np
import pandas as pd
import tensorflow as tf
from rdkit import Chem
from rdkit.Chem import AllChem, QED, RDConfig
from rdkit.DataStructs.cDataStructs import ConvertToNumpyArray

sys.path.append(os.path.join(RDConfig.RDContribDir, 'SA_Score'))
import sascorer

from RAscore import RAscore_XGB

def get_fingerprint(mol):
  """ Converts SMILES into Morgan fingerprint """
  fp_array = np.zeros((0,), dtype=np.int8)
  fp = AllChem.GetMorganFingerprintAsBitVect(mol, 2, nBits=256)
  ConvertToNumpyArray(fp, fp_array)
  return fp_array

def check_bioactivity(mol):
  """ Calculates predicted MIC """
  model = pickle.load(open('lgbm_model.sav', 'rb'))
  fp = get_fingerprint(mol)
  mic = model.predict([fp])
  return mic[0]

def check_qed(mol):
  """ Calculates QED-score """
  return QED.qed(mol)

def check_sascore(mol):
  """ Calculates SAScore """
  return sascorer.calculateScore(mol)

def check_rascore(mol):
  """ Calculates RAScore """
  ra_scorer = RAscore_XGB.RAScorerXGB()
  smiles = Chem.MolToSmiles(mol)
  return ra_scorer.predict(smiles)

tox_df = pd.read_csv('tox_alerts.txt', sep='\t')
def check_toxicophore(mol):
  """ Returns the number of toxicophore groups in a molecule """
  count = 0
  for smarts in tox_df.SMARTS.to_list():
    pattern = Chem.MolFromSmarts(smarts)
    if mol.HasSubstructMatch(pattern)==True:
      count += 1
  return count

def check_lipinski_ro5(mol):
  """ Checks Lipinski's rule of five for drig-like molecules """
  counter = 0
  counter += 1 if Chem.Lipinski.NumHDonors(mol) <= 5 else 0
  counter += 1 if Chem.Lipinski.NumHAcceptors(mol) <= 10 else 0
  counter += 1 if Chem.Descriptors.MolWt(mol) <= 500 else 0
  counter += 1 if Chem.Descriptors.MolLogP(mol) <= 5 else 0

  return counter >= 3

def check_lipinski_ro3(mol):
  """ Checks Lipinski's rule of three for lead-like molecules """
  counter = 0
  counter += 1 if Chem.Lipinski.NumHDonors(mol) <= 3 else 0
  counter += 1 if Chem.Lipinski.NumHAcceptors(mol) <= 3 else 0
  counter += 1 if Chem.Descriptors.MolWt(mol) <= 300 else 0
  counter += 1 if Chem.Descriptors.MolLogP(mol) <= 3 else 0

  return counter >= 3

smiles = 'CCO'
m = Chem.MolFromSmiles(smiles)

df = pd.DataFrame()
df['bioactivity'] = check_bioactivity(m)
df['QED'] = check_qed(m)
df['sascore'] = check_sascore(m)
df['rascore'] = check_rascore(m)
df['lipinski_ro5'] = check_lipinski_ro5(m)
df['lipinski_ro3'] = check_lipinski_ro3(m)
df['tox_groups'] = check_toxicophore(m)

df.to_csv('result.csv', index=False)

