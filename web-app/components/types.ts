export type Profile = {
  id: number;
  username: string | null;
  display_name: string | null;
  location: string | null;
  languages: string[] | null;
  github_handle: string | null;
  linkedin_handle: string | null;
  twitter_handle: string | null;
  telegram_handle: string | null;
  i_am_a_roles: string[] | null;
  interested_in_topics: string[] | null;
  about: string | null;
  current_position: string | null;
  is_university_student: boolean | null;
};

export type ProfilesFilter = {
  search: string;
  location: string;
  language: string;
  role: string;
  topic: string;
  isUniversityStudent: string;
};


