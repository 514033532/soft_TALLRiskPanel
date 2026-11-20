TALLRiskPanel 桌面版（Ubuntu/Linux 图形版）
==========================================
独立发布包（2026-11-09 构建，PyInstaller 单文件，内嵌模型）

文件：
  TALLRiskPanel_Desktop   图形版程序（Linux x86_64 可执行文件）
  model_params.json       模型参数（可放程序旁覆盖更新，可选）
  tallrisk_hgb.joblib     梯度提升决策树引擎（可选）
  report_generator.py     检测报告生成模块（可选，供二次开发）
  example_single_sample.tsv    单样本测试数据
  example_multi_sample_13.tsv  多样本测试数据

运行：
  chmod +x TALLRiskPanel_Desktop
  ./TALLRiskPanel_Desktop

功能：
  · 登录密码：默认 123456（登录后可修改，保存为程序旁 password.txt）
  · 显示语言：登录界面切换 中文 / English
  · 上传基因表达矩阵（csv/tsv/xlsx，基因在行或列）→ 16 基因自动提取
    → 按参考队列自适应标准化 → 双引擎分层（线性 0.594 + HGB 0.442）
    → 高/低危 + 临界标记 → 检验报告样式 A4 PDF（中英文随界面语言）+ CSV 导出
  · 所有计算在本地完成，数据不上传服务器

参考队列：TARGET / Cohort1 / Cohort2 / Combined
（未知队列归属时选 Combined）

多队列验证记录（写入 model_params.json validation 字段）：
  本地：本地队列1 n=13（Spearman 0.681, p=0.010）、本地队列2 ID直验 n=34
        （Spearman 0.393, p=0.021）、两队列合并 n=47（Spearman 0.507, p=2.7e-4）
  公共：GSE26713 n=117（跨平台芯片，亚型方向 p=0.0001）、GSE161896 PDX
        （ETP vs 非ETP p=1.3e-51）、SCPCP000003（30 ETP vs 11 非ETP, p=0.0039）、
        GSE227122（5/5 治疗动态）、GSE154109/GSE132509/GSE248287（特异性）、
        GSE168594（治疗后残留，描述性）

免责声明：输出供医疗专业人员参考，不构成诊断结论。

Windows 版：见 ../desktop/build_exe.bat（在 Windows 机器上打包 EXE）
命令行版：../tallriskpanel.py（python 直接运行）
