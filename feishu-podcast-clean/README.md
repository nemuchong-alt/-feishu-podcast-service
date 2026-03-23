# 飞书播客中转服务

接收 Dify Workflow 发来的结构化 JSON，写入飞书多维表。

## 功能

- 提供 `POST /api/save-podcast` 接口
- 自动获取飞书 tenant_access_token
- 写入 4 张飞书多维表：
  - 播客主表
  - 主观点表
  - 关键概念表
  - 资料线索表

## 快速开始

### 1. 安装依赖

```bash
cd feishu-podcast-service
pip install -r requirements.txt
```

### 2. 配置环境变量

```bash
cp .env.example .env
```

编辑 `.env` 文件，填入你的飞书配置：

```env
# 飞书应用凭证（需要在飞书开放平台创建应用并获取）
FEISHU_APP_ID=cli_xxxxxxxxxxxxxx
FEISHU_APP_SECRET=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
FEISHU_APP_TOKEN=xxxxxxxxxx

# 飞书多维表 ID（4 张表的 table_id）
FEISHU_TABLE_ID_PODCAST=xxxxxxxxxx
FEISHU_TABLE_ID_MAIN_POINTS=xxxxxxxxxx
FEISHU_TABLE_ID_CONCEPTS=xxxxxxxxxx
FEISHU_TABLE_ID_RESOURCES=xxxxxxxxxx
```

### 3. 本地运行

```bash
python -m app.main
```

服务将在 http://localhost:8000 启动。

### 4. 测试接口

```bash
curl -X POST http://localhost:8000/api/save-podcast \
  -H "Content-Type: application/json" \
  -d '{
    "podcast_title": "无人知晓 E45 孟岩对话李继刚：人何以自处",
    "display_markdown": "给人看的 Markdown 内容",
    "structured_json": {
      "podcast": {
        "summary": "这期播客的简短总结",
        "relisten_level": "高"
      },
      "main_points": [
        {
          "seq": 1,
          "content": "主观点内容",
          "tags": ["认知", "方法论"],
          "important": true
        }
      ],
      "concepts": [
        {
          "name": "贝叶斯定理",
          "meaning_in_episode": "在本期中的简要含义",
          "discipline": "认知科学",
          "concept_type": "理论",
          "source_type": "未提及",
          "source_name": "",
          "source_clarity": "未提及",
          "why_worth_learning": "帮助理解如何更新认知",
          "main_point_seq": 1
        }
      ],
      "resources": [
        {
          "name": "《Build》",
          "main_point_seq": 1,
          "concept_name": "产品思维",
          "resource_type": "书籍",
          "quote": "原文提到……",
          "source_clarity": "明确",
          "why_worth_checking": "适合延展阅读",
          "priority": "高"
        }
      ]
    }
  }'
```

成功响应：

```json
{
  "success": true,
  "message": "saved",
  "podcast_record_id": "xxx"
}
```

### 5. 验证服务

```bash
# 健康检查
curl http://localhost:8000/health
# 返回: {"status":"ok"}
```

## 飞书配置说明

### 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 创建企业自建应用
3. 获取 `App ID` 和 `App Secret`
4. 在应用的"权限管理"中添加以下权限：
   - `bitable:database:record:create` - 创建多维表记录
   - `bitable:database:record:read` - 读取多维表记录
   - `bitable:database:read` - 读取多维表

### 创建多维表

创建 4 张多维表，字段映射如下：

#### 播客主表
| 字段名 | 类型 |
|--------|------|
| 播客-期数 | 文本 |
| 总结 | 文本 |
| 推荐复听程度 | 单选 |

#### 主观点表
| 字段名 | 类型 |
|--------|------|
| 所属播客 | 关联记录（指向播客主表） |
| 主观点序号 | 数字 |
| 主观点内容 | 文本 |
| 主观点标签 | 多选 |
| 重要 | 开关 |

#### 关键概念表
| 字段名 | 类型 |
|--------|------|
| 概念名 | 文本 |
| 在本期中的简要含义 | 文本 |
| 学科方向 | 单选 |
| 概念类型 | 单选 |
| 来源类型 | 单选 |
| 来源名称/描述 | 文本 |
| 来源是否明确 | 单选 |
| 为什么值得补课 | 文本 |
| 所属播客 | 关联记录（指向播客主表） |
| 对应主观点 | 关联记录（指向主观点表） |

#### 资料线索表
| 字段名 | 类型 |
|--------|------|
| 资料名称 | 文本 |
| 对应主观点 | 关联记录（指向主观点表） |
| 对应概念 | 关联记录（指向关键概念表） |
| 资料类型 | 单选 |
| 原文对应摘取 | 文本 |
| 来源是否明确 | 单选 |
| 为什么值得看 | 文本 |
| 优先级 | 单选 |
| 所属播客 | 关联记录（指向播客主表） |

## Dify 配置

在 Dify Workflow 中添加 HTTP 节点，配置如下：

- **URL**: `https://你的服务域名/api/save-podcast`
- **Method**: POST
- **Body**: JSON

## 部署到 Render

### 方式一：Blueprints（推荐，自动读取 render.yaml）

1. Fork 本仓库到 GitHub
2. 登录 [Render](https://render.com)
3. 点击 **New +** → **Blueprint**
4. 连接 GitHub 仓库
5. Render 会自动读取 `render.yaml`，在 Environment 页面填入以下环境变量：

| 环境变量 | 值（示例） |
|----------|-----------|
| FEISHU_APP_ID | cli_xxxxxxxxxxxxxx |
| FEISHU_APP_SECRET | xxxxxxxxxxxxxxxxxxxxxxxx |
| FEISHU_DATABASE_ID | P0pabCuTJaIKsRsxRedcR2Kwn3d |
| FEISHU_TABLE_ID_PODCAST | tblhZXsZ6Ie0511X |
| FEISHU_TABLE_ID_MAIN_POINTS | tblKKboiJSqFPm87 |
| FEISHU_TABLE_ID_CONCEPTS | tbloBFsg7Ly29BSM |
| FEISHU_TABLE_ID_RESOURCES | tblXZMaE8Fmw18RX |

6. 点击 **Apply**

### 方式二：手动部署

1. Fork 本仓库到 GitHub
2. 登录 [Render](https://render.com)
3. 点击 **New +** → **Web Service**
4. 连接 GitHub 仓库
5. 设置：

| 配置项 | 值 |
|--------|-----|
| Region | Singapore（亚洲延迟低） |
| Branch | main |
| Runtime | Python |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `uvicorn app.main:app --host 0.0.0.0 --port $PORT` |

6. 在 Environment 添加上方表格中的所有环境变量
7. 点击 **Create Web Service**

部署完成后，Dify HTTP Request 节点填入：
```
https://你的服务名.onrender.com/api/save-podcast
```

### 方式三：Docker

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["python", "-m", "app.main"]
```

### 方式三：云服务器

```bash
# 使用 gunicorn（推荐生产环境）
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

## 注意事项

1. 第一版不做去重，重复调用会创建多条记录
2. 第一版不做更新已有记录
3. 第一版不做外部链接自动补全
4. 关联字段需要先有主表记录才能建立关联
