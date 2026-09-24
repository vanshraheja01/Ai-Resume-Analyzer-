import { ResumeDetailClient } from "./resume-detail-client";

export default async function ResumeDetailPage(props: PageProps<"/resumes/[id]">) {
  const { id } = await props.params;
  return <ResumeDetailClient id={id} />;
}
