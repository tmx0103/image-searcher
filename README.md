# 概述
本工具是使用Python开发的图文搜图工具。支持使用已有的图片搜索相似图，或者使用文本搜索相似图。目前该工具尚未完成，仅提供一个基础demo，并且需要您按照使用说明，手动完成全部准备工作后才可使用。

该工具的基本原理是通过特征提取模型（多模态模型）提取图片特征和文字特征，通过对输入的图片或文字，以及图库中图片的特征向量进行余弦相似度计算，从而从图库中寻找最相似的图片（1：N）。

图库中图片特征向量存储在Postgresql中。


# 使用说明
使用前需要完成以下工作：

+ 具备显存>=6GB的NVIDIA显卡，能够运行transformers以便运行Chinese-CLIP模型（后续会支持/使用其他模型），并已安装cuda。
+ Postgresql数据库准备
    - 已在本地或云上部署Postgresql，且安装了pgvector插件；
    - 根据app/.env-sample中的提示填写数据库相关信息，并更名为app/.env；
    - 根据.env中POSTGRESQL_DB的配置（假设配置为aidb），在Postgresql中建立对应的数据库。建立schema=dev，table=tb_img_vector，并为tb_img_vector表启用pgvector插件；
    - 建立表结构，并赋权：

```sql
create table if not exists dev.tb_img_vector
(
    id                serial
        constraint tb_img_vector_pk
            primary key,
    gmt_create        timestamp,
    img_vec           vector(1024),
    file_dir          varchar(1000),
    file_gmt_modified timestamp,
    file_name         varchar(1000),
    file_sha256       varchar(128)
);
create index if not exists tb_img_vector_file_hash_sha256_index
    on dev.tb_img_vector (file_sha256);
    
alter table dev.tb_img_vector
    owner to user1; ---user1需要替换为.env中POSTGRESQL_USER的配置


```

+ 图库准备
    - 将需要检索的所有图片（目前支持jpg、jpeg、png、gif）<font style="color:#DF2A3F;">复制</font>到app/resources/dataset目录中，<font style="color:#DF2A3F;">后续步骤将对dataset目录进行清洗和索引建立，过程中可能变更、删除dataset目录中的图片，请务必保留原来的图片</font>；
    - 执行dataset_preprocessing_rename.py，将dataset目录中的图片统一命名；
    - 执行dataset_preprocessing_load_db.py，为dataset目录中的图片建立向量索引。索引将被存放到Postgresql中。

在完成上述准备后，后续只需执行test_find_similar_img_by_img_gui.py，即可启动图文搜图工具。

+ 如果向dataset目录中新增图片，需要重新执行dataset_preprocessing_rename.py和dataset_preprocessing_load_db.py。
+ 如果自行变更dataset目录中的图片位置（比如dataset/图库1中的图片移动到dataset/图库2），请执行dataset_preprocessing_repair_file_dir.py，修复数据库中的图片索引。



