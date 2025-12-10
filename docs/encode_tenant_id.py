import argparse
import base64
import uuid


def encode_tenant_id_to_base64_url(tenant_id):
    guid = uuid.UUID(tenant_id)
    base64_url = base64.urlsafe_b64encode(guid.bytes_le).rstrip(b"=").decode("ascii")
    return base64_url


def parse_args():
    parser = argparse.ArgumentParser(
        description="Encode a tenant id to base64 URL-safe format."
    )
    parser.add_argument("--tenant_id", type=str, help="The tenant ID to encode.")
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    encoded_tenant_id = encode_tenant_id_to_base64_url(args.tenant_id)
    print(f"Encoded tenant ID: {encoded_tenant_id}")
