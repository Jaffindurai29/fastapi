import { Link } from "react-router-dom";
import { homeFor, useAuth } from "../auth";

export default function ForbiddenPage() {
  const { user } = useAuth();
  return (
    <section className="center-note">
      <h2>403: Not allowed</h2>
      <p className="muted">Your role ({user.role}) can't open that page.</p>
      <Link className="btn inline-btn" to={homeFor(user)}>
        Go to my home page
      </Link>
    </section>
  );
}
