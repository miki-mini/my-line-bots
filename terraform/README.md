# Terraform for My LINE Bots

このディレクトリには、プロジェクトのGoogle Cloudインフラストラクチャを管理するためのTerraform設定ファイルが含まれています。

記事で紹介されていた推奨構成（Artifact Registry, Cloud Run, Secret Manager, Workload Identity Federation）をコード（Infrastructure as Code）として定義しています。

## 1. Infrastructure as Code (IaC) とは？

これまで `gcloud` コマンドやコンソールで手動で行っていた設定を、コードとして記述し管理する手法です。
メリット：
- **再現性**: 誰が実行しても同じ環境が作れます。
- **バージョン管理**: インフラの変更履歴をGitで管理できます。
- **一貫性**: 設定ミスや「環境による違い」を防げます。

## 2. 記事の手順とTerraformの対応

記事で紹介された手動コマンドが、どのTerraformファイルに対応しているかの一覧です。

| 記事の手順 / gcloud コマンド | Terraform ファイル | リソース名 |
|---------------------------|-------------------|-----------|
| `gcloud artifacts repositories create ...` | `artifact_registry.tf` | `google_artifact_registry_repository.repo` |
| `gcloud run deploy ... --set-secrets=...` | `cloud_run.tf` | `google_cloud_run_v2_service.voidoll_bot` |
| `gcloud secrets create ...` | `secrets.tf` | `google_secret_manager_secret` |
| `gcloud secrets add-iam-policy-binding ...` | `iam.tf` | `google_project_iam_member.secret_accessor` |
| WIFプールの作成 (gcloud iam workload-identity-pools ...) | `iam.tf` | `google_iam_workload_identity_pool` |
| サービスアカウント作成 | `iam.tf` | `google_service_account` |

## 3. 使い方

### 前提条件
- [Terraform](https://developer.hashicorp.com/terraform/install) がインストールされていること。
- Google Cloud SDK (`gcloud`) がインストールされ、認証済みであること (`gcloud auth application-default login`)。

### 手順

1. **初期化**
   Terraformに必要なプラグインをダウンロードします。
   ```bash
   cd terraform
   terraform init
   ```

2. **変数の設定**
   `terraform.tfvars` というファイルを作成し、自分のプロジェクトIDなどを設定します。
   ```hcl
   # terraform.tfvars
   project_id = "your-project-id"
   region     = "asia-northeast1"
   ```

3. **計画の確認 (Dry Run)**
   どのような変更が行われるかを確認します。実際に変更は行われません。
   ```bash
   terraform plan
   ```

4. **適用の実行**
   実際にGoogle Cloudにリソースを作成・変更します。
   ```bash
   terraform apply
   ```

## 4. CI/CD との関係

このTerraform設定は、**「アプリケーションが動くための土台（インフラ）」** を作ります。
一方、既存の GitHub Actions は、**「その土台の上でアプリケーションを更新・デプロイ」** します。

- **Terraformの役割**:
  - Artifact Registryを作る
  - Cloud Runサービス（の枠組み）を作る
  - 権限（IAM）を設定する
  - GitHub Actionsがデプロイできるようにする (WIF設定)

- **GitHub Actionsの役割**:
  - コードをテストする
  - Dockerイメージをビルドする
  - Artifact Registryにプッシュする
  - Cloud Runに新しいイメージをデプロイする

したがって、最初にTerraformで `apply` を実行して環境を整えれば、あとはこれまで通り GitHub Actions で日々の開発・デプロイを回すことができます。
