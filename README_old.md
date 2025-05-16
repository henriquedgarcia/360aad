# 360VPSC - 360° DASH-SRD video playback session characterization with HEVC

## Sumário

Este repositório apresenta os scripts usados para processar o banco de dados criado com várias métricas para a caracterização de seção de reprodução de streaming de video 360°. 

Dataset disponível em https://www.dropbox.com/sh/teyex6piishj1pk/AABNcSCmjrK7ioQ1Y3IQnORZa?dl=0

Os vídeos usados são os mesmos do artigo https://dl.acm.org/doi/abs/10.1145/3304109.3325812. Os vídeos são classificados de acordo com a movimentação da câmera e a quantidade de pontos de interesse distribuidos pela cena.

Para simular uma seção de streaming com DASH SRD os vídeos em projeção equirretangular foram recordados em vários padrões de ladrilhamento diferentes, codificados em várias qualidades diferentes com CRF '0', 16, 22, 28, 34, 40 e 46 e segmentados em chunks de 1 segundo. A taxa de bits, tempo de codificação e a distorção de codificação (erro quadrático médio) foram calculadas para cada chunk. As métricas objetivas de qualidade são MSE, WS-MSE e S-MSE. Para cada vídeo sem ladrilhamento, codificado com CRF 28 foi calculada a informação espacial e temporal (SITI).

Usando o banco de dados de movimento de cabeça do trabalho de Nasrabadi, para cada usuário foram calculados quais tiles seriam requisitados para cada padrão de segmentação de ladrilhos, entre: 1x1 (sem ladrilhamento), 3x2, 6x4, 9x6 e 12x8. Além disso, o viewport de cada usuário para cada qualidade e cada padrão de segmentação foi reconstruído e seu PSNR foi calculado em função do vídeo sem compressão e sem ladrilhamento.

Usando os ladrilhos visualizados e as métricas calculadas é possível caracterizar e estimar o limite inferior de recursos como tempo de decodificação, largura de banda e qualidade esperada mínima para cada usuário assistindo os vídeos em cada qualidade e em cada ladrilhamento. 

A estrutura do projeto é:
```
360VPSC  
 |-data  
 |  |-erp  
 |     |- bitrate               # dados sobre a taxa de bits de cada chunk  
 |     |- dectime               # dados sobre o tempo de decodificação de cada chunk  
 |     |- get_tiles             # dados sobre os ladrilhos visualizados para cada usuário  
 |     |- quality_chunks        # dados sobre a qualidade objetivada para cada chunk  
 |     |- quality_viewport      # dados sobre a qualidade objetiva do viewport de cada usuário  
 |     |- siti                  # dados sobre a informação espacial e temporal de cada vídeo com CRF 28  
 |-graphs  
 |-lib  
 |  |-erp  
 ```