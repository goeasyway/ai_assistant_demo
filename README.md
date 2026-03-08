# ai_assistant_demo

基于 [Chainlit](https://docs.chainlit.io) 和 [Claude Agent SDK](https://github.com/anthropics/claude-agent-sdk) 构建的 AI 办公助手，提供 Web 聊天界面，可帮助用户处理办公文档（Excel、Word、PDF）等任务。

## 功能特性

- **对话式交互**：通过 Web 界面与 AI 助手进行多轮对话
- **会话保持**：同一会话内自动保持上下文连续性
- **文件上传**：支持上传文件作为附件，AI 可读取并处理
- **办公文档处理**：可创建和处理 Excel、Word、PDF 等办公文档
- **工具调用可视化**：在界面中展示 AI 的思考过程和工具调用详情
- **流式输出**：实时流式展示 AI 回复内容

## 使用
pip install chainlit
pip install claude_agent_sdk

开启热重载（开发模式）：
```bash
chainlit run app.py -w
```
启动后，浏览器会自动打开 Web 界面（默认地址：`http://localhost:8000`）。

演示视频 ai_assistant_demo.mp4
<video id="video" controls="" preload="none" poster="演示视频">
    <source id="mp4" src="ai_assistant_demo.mp4" type="video/mp4">
</videos>

## 系列文章

本项目属于[《不用龙虾，我用100行代码做了一个AI Agent平台》]()文章使用的源码，关注公众号获取更多内容:

**AI Native启示录**

<img src="images/qrcode.jpg" width="200" />
