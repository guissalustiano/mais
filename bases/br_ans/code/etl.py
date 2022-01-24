import pandas as pd
from ftp import ReaderFtp

host = ReaderFtp('ftp.dadosabertos.ans.gov.br')


def process(df):
    # escrever processamento aqui
    return df

if __name__ == '__main__':
    time = datetime(2020, 1, 1)
    path = 'FTP/PDA/informacoes_consolidadas_de_beneficiarios'
    for ftpfile in list_recursive_newer(path, time):

        for filename, file in extract_fpt_zip(ftpfile):
            s3path = host.path.join(bucket_path, host.path.dirname(ftpfile), filename)
            df = pd.read_csv(file, sep=";", encoding='cp1252')
            df = process(df)

            wr.s3.to_parquet(
                df=df,
                path=s3path,
                dataset=True,
                database="ans",
                table="informacoes_consolidadas_de_beneficiarios"
            )





