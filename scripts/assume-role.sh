#!/bin/bash

# === Unified AWS Assume Role Script ===
# ✅ Works in: Local CLI, Docker, GitHub Actions
# ✅ Auto-refreshes expired creds
# ✅ Outputs to .env and current shell (optional)

ROLE_ARN=${ROLE_ARN:-"arn:aws:iam::008971663545:role/barry_allen"}
SESSION_NAME=${SESSION_NAME:-"unified-cli-session"}
DURATION_SECONDS=${DURATION_SECONDS:-3600}  # 1 hour

# === Ensure jq is installed ===
if ! command -v jq &> /dev/null; then
    echo "❌ 'jq' is required but not installed. Please install jq."
    exit 1
fi

# === Check if base credentials are valid ===
echo "🔍 Validating base credentials..."
if ! aws sts get-caller-identity &> /dev/null; then
  echo "⚠️  Base credentials are missing or expired."
  read -p "🔑 Enter AWS Access Key ID: " AWS_ACCESS_KEY_ID
  read -s -p "🔐 Enter AWS Secret Access Key: " AWS_SECRET_ACCESS_KEY
  echo
  export AWS_ACCESS_KEY_ID
  export AWS_SECRET_ACCESS_KEY

  if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ Invalid credentials. Exiting."
    exit 1
  fi
  echo "✅ Base IAM credentials are valid."
else
  echo "✅ Base IAM credentials are valid."
fi

# === Assume the Role ===
echo "🔐 Assuming role: $ROLE_ARN"
CREDS=$(aws sts assume-role \
  --role-arn "$ROLE_ARN" \
  --role-session-name "$SESSION_NAME" \
  --duration-seconds "$DURATION_SECONDS" \
  --query "Credentials" --output json)

if [ $? -ne 0 ]; then
  echo "❌ Failed to assume role."
  exit 1
fi

# === Extract credentials ===
export AWS_ACCESS_KEY_ID=$(echo "$CREDS" | jq -r '.AccessKeyId')
export AWS_SECRET_ACCESS_KEY=$(echo "$CREDS" | jq -r '.SecretAccessKey')
export AWS_SESSION_TOKEN=$(echo "$CREDS" | jq -r '.SessionToken')
EXPIRATION=$(echo "$CREDS" | jq -r '.Expiration')

# === Output to .env ===
cat <<EOF > .env
# Generated temporary credentials
ROLE_ARN=$ROLE_ARN
AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY
AWS_SESSION_TOKEN=$AWS_SESSION_TOKEN
EOF

echo "✅ Temporary credentials written to .env"
echo "⏰ Expires at: $EXPIRATION"

# === Optional: export in shell ===
if [ -z "$CI" ]; then
  read -p "📦 Export to current shell session? (y/n): " reply
  if [[ "$reply" == "y" ]]; then
    echo "✅ Credentials exported to shell."
  fi
else
  echo "🏗 Running in CI environment — auto-exported."
fi