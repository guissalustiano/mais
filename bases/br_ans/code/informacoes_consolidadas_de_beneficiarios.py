import pandas as pd
from multiprocessing import Pool
from datetime import datetime
from ftp import ReaderFtp
import logging
from pathlib import Path

logger = logging.getLogger()


host = ReaderFtp('ftp.dadosabertos.ans.gov.br')
TABLE_NAME = 'informacoes_consolidadas_de_beneficiarios'
FTP_PATH = 'FTP/PDA/informacoes_consolidadas_de_beneficiarios'
TABLE_TYPE = {
    '#ID_CMPT_MOVEL': str,
    'CD_OPERADORA': str,
    'NM_RAZAO_SOCIAL': str,
    'NR_CNPJ': str,
    'MODALIDADE_OPERADORA': str,
    'SG_UF': str,
    'CD_MUNICIPIO': str,
    'NM_MUNICIPIO': str,
    'TP_SEXO': str,
    'DE_FAIXA_ETARIA': str,
    'DE_FAIXA_ETARIA_REAJ': str,
    'CD_PLANO': str,
    'TP_VIGENCIA_PLANO': str,
    'DE_CONTRATACAO_PLANO': str,
    'DE_SEGMENTACAO_PLANO': str,
    'DE_ABRG_GEOGRAFICA_PLANO': str,
    'COBERTURA_ASSIST_PLAN': str,
    'TIPO_VINCULO': str,
    'QT_BENEFICIARIO_ATIVO': int,
    'QT_BENEFICIARIO_ADERIDO': int,
    'QT_BENEFICIARIO_CANCELADO': int,
    'QT_BENEFICIARIO_CANCELADO': int,
    'DT_CARGA': str,
}


def process(df):
    time_col = pd.to_datetime(df['#ID_CMPT_MOVEL'], format='%Y%m')
    df['ano'] = time_col.dt.year
    df['mes'] = time_col.dt.month
    del df['#ID_CMPT_MOVEL']
    del df['NM_MUNICIPIO']
    del df['DT_CARGA']

    df.rename(columns={
        'CD_OPERADORA': 'codigo_operadora',
        'NM_RAZAO_SOCIAL': 'nome_razao_social',
        'NR_CNPJ': 'cnpj',
        'MODALIDADE_OPERADORA': 'modalidade_operadora',
        'SG_UF': 'sigla_uf',
        'CD_MUNICIPIO': 'id_municipio_6',
        'TP_SEXO': 'sexo',
        'DE_FAIXA_ETARIA': 'faixa_etaria',
        'DE_FAIXA_ETARIA_REAJ': 'faixa_etaria_real',
        'CD_PLANO': 'codigo_plano',
        'TP_VIGENCIA_PLANO': 'tipo_vigencia_plano',
        'DE_CONTRATACAO_PLANO': 'contratacao_plano',
        'DE_SEGMENTACAO_PLANO': 'segmento_plano',
        'DE_ABRG_GEOGRAFICA_PLANO': 'abrangencia_geografica_plano',
        'COBERTURA_ASSIST_PLAN': 'cobertura_assistencia_plano',
        'TIPO_VINCULO': 'tipo_vinculo',
        'QT_BENEFICIARIO_ATIVO': 'qtd_beneficiario_ativo',
        'QT_BENEFICIARIO_ADERIDO': 'qtd_beneficiario_aderido',
        'QT_BENEFICIARIO_CANCELADO': 'qtd_beneficiario_cancelado',
        'QT_BENEFICIARIO_CANCELADO': 'qtd_beneficiario_cancelado'
    }, inplace=True)

    df['cnpj'] = df['cnpj'].str.zfill(14)
    df['cnpj'] = df['cnpj'].str.zfill(14)
    return df

def read_all_csv_zip(basepath):
    paths = host.list_newer(basepath)
    return [host.read_csv_zip(p) for p in paths if p.endswith('.zip')]

def read_all_csv_zip_df(basepath):
    files = read_all_csv_zip(basepath)
    dfs = [pd.read_csv(fc, sep=";", encoding='cp1252', dtype=TABLE_TYPE) for fn, fc in files]
    return pd.concat(dfs, axis=0, ignore_index=True)

def load(df: pd.DataFrame):
    year = df['ano'].unique()[0]; del df['ano']
    month = df['mes'].unique()[0]; del df['mes']
    uf = df['sigla_uf'].unique()[0]; del df['sigla_uf']
    path = Path('../output') / TABLE_NAME / f'ano={year}' / f'mes={month}' / f'sigla_uf={uf}' / f'ben{year}{month}_{uf}.parquet'
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path)

def etl_yearmount(path):
    logger.info(f'extract dataframe {path}')
    df = read_all_csv_zip_df(path)

    logger.info(f'processing dataframe {path}')
    df = process(df)

    logger.info(f'load dataframe {path}')
    load(df)

def etl_all():
    for path in host.list_newer(FTP_PATH):
        if 'dicionario' in path:
            continue
        etl_yearmount(path)

def etl_each():
    for paths in host.list_newer(FTP_PATH):
        if 'dicionario' in paths:
            continue
        for path in host.list_newer(paths):
            if not path.endswith('.zip'):
                continue

            logger.info(f'extract dataframe {path}')
            filename, filecontent = host.read_csv_zip(path) 
            df = pd.read_csv(filecontent, sep=";", encoding='cp1252', dtype=TABLE_TYPE)

            logger.info(f'processing dataframe {path}')
            df = process(df)

            logger.info(f'load dataframe {path}')
            load(df)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    etl_each()
