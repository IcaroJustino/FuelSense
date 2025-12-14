export interface AuthToken {
  access_token: string;
  token_type: string;
}

export interface LoginPayload {
  email: string;
  senha: string;
}

export interface UserInfo {
  id: number;
  nome: string;
  email: string;
  cpf: string;
  coreid: string;
}
